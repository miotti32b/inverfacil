
# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'calculadora/home.html')


from django.shortcuts import render

def calculadora_interes_compuesto(request):
    if request.method == "POST":
        # Obtener los datos del formulario
        principal = float(request.POST.get('principal', 0))
        additional_investment = float(request.POST.get('additional_investment', 0))
        investment_period = request.POST.get('investment_period')
        time = float(request.POST.get('time', 0))
        time_period = request.POST.get('time_period')
        rate = float(request.POST.get('rate', 0)) / 100
        rate_period = request.POST.get('rate_period')

        # Determinar el número total de períodos
        if time_period == 'daily':
            total_periods = int(time)
        elif time_period == 'weekly':
            total_periods = int(time * 7)
        elif time_period == 'monthly':
            total_periods = int(time * 365/12)
        else:  # yearly
            total_periods = int(time * 365)

        # Inicializar el monto total con la inversión inicial
        total_amount = principal

        # Ajuste para la aplicación del interés compuesto
        if rate_period == 'daily':
            rate_per_period = rate
        elif rate_period == 'weekly':
            rate_per_period = rate / 7
        elif rate_period == 'monthly':
            rate_per_period = rate / 30
        else:  # yearly
            rate_per_period = rate / 365

        # Iterar sobre cada período total
        for period in range(1, total_periods + 1):
            # Aplicar la inversión adicional según la frecuencia seleccionada
            if (investment_period == 'daily' and period % 1 == 0) or \
               (investment_period == 'weekly' and period % 7 == 0) or \
               (investment_period == 'monthly' and period % 30 == 0) or \
               (investment_period == 'yearly' and period % 365 == 0):
                total_amount += additional_investment

            # Aplicar la tasa de interés solo si es mayor a 0
            if rate > 0:
                total_amount *= (1 + rate_per_period)

        # Pasar el resultado a la plantilla
        return render(request, 'calculadora/calculadora.html', {
            'amount': round(total_amount, 2),
            'principal': principal,
            'additional_investment': additional_investment,
            'investment_period': investment_period,
            'time': time,
            'time_period': time_period,
            'rate': rate * 100,
            'rate_period': rate_period
        })
    return render(request, 'calculadora/calculadora.html')

