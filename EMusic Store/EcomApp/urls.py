from django.urls import path
from .views import Home, product_single, category_product, About, contact, SearchView, Faq_details
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', Home, name='home'),
    path('about/', About, name='about'),
    path('contact/', contact, name='contact_dat'),
    path('product/<int:id>/', product_single, name='product_single'),
    path('product/<int:id>/<slug:slug>/', category_product, name='category_product'),
    path('search/', SearchView, name='SearchView'),
    path('faq/', Faq_details, name='Faq_details'),

]
if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)