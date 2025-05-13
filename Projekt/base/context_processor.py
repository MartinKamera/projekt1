from base.models import Portfolio

def user_portfolios(request):
    if request.user.is_authenticated:
        return {'user_portfolios': Portfolio.objects.filter(user=request.user)}
    return {'user_portfolios': []}