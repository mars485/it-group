class CampaignMiddleware:
    KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        for key in self.KEYS:
            value = request.GET.get(key)
            if value:
                request.session[f"campaign_{key}"] = value[:160]
        return self.get_response(request)
