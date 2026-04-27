from handlers import sevimlilar, start, profile, settings # Hammasini import qilamiz

# Dispatcherga ulaymiz
dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(settings.router)
dp.include_router(sevimlilar.router) # Sevimlilar routerni ulash
