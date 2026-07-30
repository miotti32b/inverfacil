from decimal import Decimal

import requests
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date

from calculadora.models import BlueDollarRate


class Command(BaseCommand):
    help = "Importa historico de dolar blue desde Bluelytics."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Simula la importacion sin guardar.")
        parser.add_argument("--timeout", type=int, default=45)
        parser.add_argument("--batch-size", type=int, default=1000)

    def handle(self, *args, **options):
        url = "https://api.bluelytics.com.ar/v2/evolution.json"
        try:
            response = requests.get(url, timeout=options["timeout"])
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise CommandError(f"No pude conectar con Bluelytics: {exc}") from exc
        except ValueError as exc:
            raise CommandError("Bluelytics no devolvio JSON valido.") from exc

        rows = []
        for item in payload:
            if item.get("source") != "Blue":
                continue
            day = parse_date(str(item.get("date") or ""))
            if not day:
                continue
            rows.append({
                "date": day,
                "buy": Decimal(str(item.get("value_buy") or "0")),
                "sell": Decimal(str(item.get("value_sell") or "0")),
            })

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Dolar blue detectado: {len(rows)} fechas."))
            return

        batch_size = max(int(options["batch_size"] or 1000), 100)
        existing_by_date = {
            rate.date: rate
            for rate in BlueDollarRate.objects.filter(date__in=[row["date"] for row in rows])
        }
        to_create = []
        to_update = []
        for row in rows:
            existing = existing_by_date.get(row["date"])
            if existing:
                existing.buy = row["buy"]
                existing.sell = row["sell"]
                existing.source = "Bluelytics"
                to_update.append(existing)
            else:
                to_create.append(
                    BlueDollarRate(
                        date=row["date"],
                        buy=row["buy"],
                        sell=row["sell"],
                        source="Bluelytics",
                    )
                )

        with transaction.atomic():
            if to_create:
                BlueDollarRate.objects.bulk_create(to_create, batch_size=batch_size, ignore_conflicts=True)
            if to_update:
                BlueDollarRate.objects.bulk_update(to_update, ["buy", "sell", "source"], batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS(f"Dolar blue listo: nuevos={len(to_create)}, actualizados={len(to_update)}."))
