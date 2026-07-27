import csv
import hashlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from calculadora.models import NaifCost, NaifSale


PRODUCT_NAMES = {
    "1": "Arabes",
    "2": "Saladas",
    "3": "Dulces",
    "4": "Pollo",
    "5": "Jamon y queso",
    "6": "Salame y muzza",
    "7": "Fugazza",
    "8": "Abiertas",
    "9": "caprese",
    "10": "picantes",
    "11": "envio",
}


class Command(BaseCommand):
    help = "Importa el historico NAIF desde los CSV de ventas y costos sin duplicar registros."

    def add_arguments(self, parser):
        parser.add_argument("--ventas", required=True, help="Ruta al CSV NAIF - NUEVO SISTEMA.csv")
        parser.add_argument("--costos", required=True, help="Ruta al CSV NAIF - COSTOS.csv")
        parser.add_argument("--dry-run", action="store_true", help="Procesa los archivos sin guardar cambios")
        parser.add_argument("--batch-size", type=int, default=1000, help="Cantidad de filas por lote de insercion")

    def handle(self, *args, **options):
        ventas_path = Path(options["ventas"]).expanduser()
        costos_path = Path(options["costos"]).expanduser()
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]

        if not ventas_path.exists():
            raise CommandError(f"No existe el archivo de ventas: {ventas_path}")
        if not costos_path.exists():
            raise CommandError(f"No existe el archivo de costos: {costos_path}")

        subtotal_deleted = self.clean_cost_subtotals(dry_run)
        sale_totals_fixed = self.fix_sale_totals(dry_run)
        product_names_fixed = self.fix_product_names(dry_run)
        ventas = self.import_sales(ventas_path, dry_run, batch_size)
        costos = self.import_costs(costos_path, dry_run, batch_size)

        mode = "simulados" if dry_run else "guardados"
        self.stdout.write(self.style.SUCCESS(
            f"Importacion NAIF lista: ventas {mode}={ventas['created']}, "
            f"costos {mode}={costos['created']}, duplicados={ventas['skipped'] + costos['skipped']}, "
            f"subtotales_total_limpiados={subtotal_deleted}, ventas_total_reparadas={sale_totals_fixed}, "
            f"productos_actualizados={product_names_fixed}"
        ))

    def clean_cost_subtotals(self, dry_run):
        subtotal_qs = NaifCost.objects.exclude(import_key__isnull=True).filter(
            Q(category__iexact="TOTAL") | Q(item__iexact="TOTAL")
        )
        count = subtotal_qs.count()
        if not dry_run and count:
            subtotal_qs.delete()
        return count

    def fix_sale_totals(self, dry_run):
        broken_qs = NaifSale.objects.filter(total=0, quantity__gt=0, unit_price__gt=0)
        count = broken_qs.count()
        if not dry_run and count:
            for sale in broken_qs.iterator(chunk_size=1000):
                sale.total = sale.quantity * sale.unit_price
                sale.save(update_fields=["total"])
        return count

    def fix_product_names(self, dry_run):
        fixed = 0
        for code, name in PRODUCT_NAMES.items():
            product_qs = NaifSale.objects.filter(product_code=code).exclude(product_name=name)
            count = product_qs.count()
            fixed += count
            if not dry_run and count:
                product_qs.update(product_name=name)
        return fixed

    def import_sales(self, path, dry_run, batch_size):
        sale_rows = []
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row_number, row in enumerate(reader, start=2):
                date = parse_date(row.get("FECHA"))
                client = clean_text(row.get("CLIENTE"))
                code = clean_text(row.get("VARIEDAD"))
                quantity = parse_money(row.get("CANTIDAD"))
                unit_price = parse_money(row.get(" PRECIO DOCENA") or row.get("PRECIO DOCENA"))
                total = parse_money(row.get(" TOTAL") or row.get("TOTAL"))
                if not date or not client or not code:
                    continue
                if quantity <= 0 and total <= 0:
                    continue

                product_name = PRODUCT_NAMES.get(code, code)
                if quantity <= 0 and unit_price > 0 and total > 0:
                    quantity = total / unit_price
                if unit_price <= 0 and quantity > 0 and total > 0:
                    unit_price = total / quantity
                key = stable_key("sale", date, client, code, quantity, unit_price, total, row_number)
                sale_rows.append({
                    "import_key": key,
                    "source_file": path.name,
                    "date": date,
                    "client": client,
                    "product_code": code,
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": quantity * unit_price,
                })
        existing = set(
            NaifSale.objects.filter(import_key__in=[row["import_key"] for row in sale_rows])
            .values_list("import_key", flat=True)
        )
        new_rows = [row for row in sale_rows if row["import_key"] not in existing]
        if not dry_run and new_rows:
            NaifSale.objects.bulk_create(
                [
                    NaifSale(
                        import_key=row["import_key"],
                        source_file=row["source_file"],
                        date=row["date"],
                        client=row["client"],
                        product_code=row["product_code"],
                        product_name=row["product_name"],
                        quantity=row["quantity"],
                        unit_price=row["unit_price"],
                        total=row["total"],
                        paid=True,
                        notes="Importado desde CSV historico",
                    )
                    for row in new_rows
                ],
                batch_size=batch_size,
                ignore_conflicts=True,
            )
        created = len(new_rows)
        skipped = len(sale_rows) - created
        return {"created": created, "skipped": skipped}

    def import_costs(self, path, dry_run, batch_size):
        cost_rows = []
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))
        if not rows:
            return {"created": 0, "skipped": 0}

        header = rows[0]
        dates = [parse_date(cell) for cell in header[2:]]
        for row_number, row in enumerate(rows[1:], start=2):
            if len(row) < 3:
                continue
            category = clean_text(row[0])
            item = clean_text(row[1]) or category
            if not item:
                continue
            if category.upper() == "TOTAL" or item.upper() == "TOTAL":
                continue
            for offset, amount_raw in enumerate(row[2:]):
                if offset >= len(dates):
                    break
                date = dates[offset]
                amount = parse_money(amount_raw)
                if not date or amount <= 0:
                    continue
                key = stable_key("cost", date, category, item, amount)
                cost_rows.append({
                    "import_key": key,
                    "source_file": path.name,
                    "date": date,
                    "category": category,
                    "item": item,
                    "amount": amount,
                })
        existing = set(
            NaifCost.objects.filter(import_key__in=[row["import_key"] for row in cost_rows])
            .values_list("import_key", flat=True)
        )
        new_rows = [row for row in cost_rows if row["import_key"] not in existing]
        if not dry_run and new_rows:
            NaifCost.objects.bulk_create(
                [
                    NaifCost(
                        import_key=row["import_key"],
                        source_file=row["source_file"],
                        date=row["date"],
                        category=row["category"],
                        item=row["item"],
                        amount=row["amount"],
                        paid=True,
                        notes="Importado desde CSV historico",
                    )
                    for row in new_rows
                ],
                batch_size=batch_size,
                ignore_conflicts=True,
            )
        created = len(new_rows)
        skipped = len(cost_rows) - created
        return {"created": created, "skipped": skipped}


def clean_text(value):
    return str(value or "").strip()


def parse_date(value):
    raw = clean_text(value)
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None


def parse_money(value):
    raw = clean_text(value)
    if not raw:
        return Decimal("0")
    raw = raw.replace("$", "").replace(" ", "").replace("\xa0", "")
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        decimals = raw.rsplit(",", 1)[1]
        raw = raw.replace(",", "") if len(decimals) == 3 else raw.replace(",", ".")
    elif "." in raw:
        decimals = raw.rsplit(".", 1)[1]
        if len(decimals) == 3:
            raw = raw.replace(".", "")
    else:
        raw = raw.replace(",", ".")
    raw = raw.replace("-", "0") if raw in {"-", "--"} else raw
    try:
        return Decimal(raw or "0")
    except InvalidOperation:
        return Decimal("0")


def stable_key(*parts):
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return f"naif:{digest}"
