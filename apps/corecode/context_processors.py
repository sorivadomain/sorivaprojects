from .models import AcademicSession, AcademicTerm, Installment, SiteConfig


def site_defaults(request):
    current_session = AcademicSession.objects.get(current=True)
    current_term = AcademicTerm.objects.get(current=True)
    current_install = Installment.objects.get(current=True)
    vals = SiteConfig.objects.all()
    contexts = {
        "current_session": current_session.name,
        "current_term": current_term.name,
        "current_install": current_install.name,
    }
    for val in vals:
        contexts[val.key] = val.value

    return contexts
