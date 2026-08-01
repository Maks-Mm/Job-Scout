# #backend/app/services/collector_registry.py
# #from app.collectors.austria import AMSCollector, KarriereATCollector, WillhabenCollector
# #from app.collectors.germany import ArbeitsagenturCollector, KleinanzeigenCollector, StepStoneCollector, StellenanzeigenCollector
# #from app.collectors.shared import AdzunaCollector, ArbeitnowCollector, JoobleCollector
# #from app.collectors.switzerland import ArbeitgeberCHCollector, JobScout24Collector, JobsCHCollector
# 
# 
# def get_collectors(country: str | None = None):
#     country_name = (country or "Germany").strip().lower()
# 
#     if country_name == "germany":
#         return [
#             ArbeitsagenturCollector(),
#             StepStoneCollector(),
#             StellenanzeigenCollector(),
#             KleinanzeigenCollector(),
#         ]
# 
#     if country_name == "austria":
#         return [
#             AMSCollector(),
#             KarriereATCollector(),
#             WillhabenCollector(),
#         ]
# 
#     if country_name == "switzerland":
#         return [
#             JobsCHCollector(),
#             JobScout24Collector(),
#             ArbeitgeberCHCollector(),
#         ]
# 
#     return [
#         AdzunaCollector(),
#         ArbeitnowCollector(),
#         JoobleCollector(),
#         ArbeitsagenturCollector(),
#         KleinanzeigenCollector(),
#         StepStoneCollector(),
#         StellenanzeigenCollector(),
#     ]
# 
# 
# def get_collector_by_source(source: str):
#     collectors = {
#         "Adzuna": AdzunaCollector,
#         "Arbeitnow": ArbeitnowCollector,
#         "Jooble": JoobleCollector,
#         "Arbeitsagentur": ArbeitsagenturCollector,
#         "Kleinanzeigen": KleinanzeigenCollector,
#         "StepStone": StepStoneCollector,
#         "Stellenanzeigen": StellenanzeigenCollector,
#         "AMS": AMSCollector,
#         "Karriere.at": KarriereATCollector,
#         "Willhaben": WillhabenCollector,
#         "jobs.ch": JobsCHCollector,
#         "JobScout24": JobScout24Collector,
#         "Arbeitgeber.ch": ArbeitgeberCHCollector,
#     }
#     return collectors.get(source)
# 
# 
# def get_all_collectors():
#     return [
#         AdzunaCollector(),
#         ArbeitnowCollector(),
#         JoobleCollector(),
#         ArbeitsagenturCollector(),
#         KleinanzeigenCollector(),
#         StepStoneCollector(),
#         StellenanzeigenCollector(),
#         AMSCollector(),
#         KarriereATCollector(),
#         WillhabenCollector(),
#         JobsCHCollector(),
#         JobScout24Collector(),
#         ArbeitgeberCHCollector(),
#     ]