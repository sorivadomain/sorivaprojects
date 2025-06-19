import logging
import os
from django.views.generic import TemplateView
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

class WebsiteHomeView(TemplateView):
    template_name = 'website/website_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Path to static/images directory
        images_dir = os.path.join(settings.STATICFILES_DIRS[0], 'images')
        # List all .jpg and .JPG files
        gallery_images = [
            f for f in os.listdir(images_dir)
            if os.path.isfile(os.path.join(images_dir, f)) and f.lower().endswith(('.jpg', '.JPG'))
        ]
        context['gallery_images'] = gallery_images
        # Staff leaders data
        context['staff_leaders'] = [
            {
                'title': 'Director',
                'name': 'Father Ferdinand Barugize',
                'image': 'IMG_3086 1.jpg',
                'phone': None
            },
            {
                'title': 'HeadMaster',
                'name': 'Kalimanzira Mbwege',
                'image': 'IMG_3293.jpg',
                'phone': '+255788395128'
            },
            {
                'title': 'SecondMaster',
                'name': 'Chef Barugize',
                'image': 'DSC_0127.JPG',
                'phone': '+255750719757'
            },
            {
                'title': 'Academic',
                'name': 'Norway Hassan',
                'image': 'DSC_0131.JPG',
                'phone': '+255680502671'
            },
            {
                'title': 'Bursar',
                'name': 'Kalimanzila Magego',
                'image': 'DSC_0135.JPG',
                'phone': '+255743023365'
            },
            {
                'title': 'Secretary',
                'name': 'Asante Hamiss',
                'image': 'DSC_0129.JPG',
                'phone': '+255781106089'
            }
        ]
        return context

    def get(self, request, *args, **kwargs):
        logger.info("Rendering WebsiteHomeView")
        return super().get(request, *args, **kwargs)
    

class WebsiteWelcomeView(TemplateView):
    template_name = 'website/website_welcome.html'

    def get(self, request, *args, **kwargs):
        logger.info("Rendering WebsiteWelcomeView")
        return super().get(request, *args, **kwargs)