"""Hardcoded list of Swedish children's stories for the story button.

Mostly Astrid Lindgren's own readings, all suitable for a 3-year-old and
roughly 15 minutes or shorter. Multi-track entries are one story split into
"Del 1-N" tracks on Spotify; the tracks are queued together and played in order.

Generated from verified Spotify data by scripts/spotify_search.py.
"""

STORIES = [
    # Bullerbyboken - Astrid Lindgren läser och berättar (Del 1-4)
    {"title": "Alla vi barn i Bullerbyn",  # 2:13
     "tracks": ["1qMyxDnZR89ZaEwmIqt0mB"]},
    {"title": "Min roligaste födelsedag",  # 5:55
     "tracks": ["6KTYKOPF7az9UlCE9o8VLH"]},
    {"title": "När vi slutade skolan",  # 5:06
     "tracks": ["0qQG3LWidaYMxlA14wiA4c"]},
    {"title": "Vi gallrar rovor och får en kattunge",  # 6:54
     "tracks": ["6gAQFLmwpGHsS6K2OJeeZX"]},
    {"title": "Hur Olle fick sin hund",  # 5:17
     "tracks": ["6dkmrulMIFlcy7NopPZmdP"]},
    {"title": "Det är roligt att få ett eget djur, men en farfar är också bra",  # 3:46
     "tracks": ["6Avz812Qesh2ftq7ZsAspD"]},
    {"title": "Pojkar kan inte ha några hemligheter",  # 7:22
     "tracks": ["6MkztZUw4uH2l5wJ0PFUQA"]},
    {"title": "Vi ligger på höskullen",  # 4:43
     "tracks": ["31Jzy6HkztQyCktCw9KF68"]},
    {"title": "När Anna och jag skulle rymma",  # 6:46
     "tracks": ["7E44rNo4JjLfoNsxgOyYSW"]},
    {"title": "Vi bygger en lekstuga",  # 2:47
     "tracks": ["6uzqygvmXgJJbFPf5tPpjb"]},
    {"title": "Det är ju det jag har sagt - pojkar kan inte ha några hemligheter",  # 5:36
     "tracks": ["2F8OThJJGq9CoCczOXRdqw"]},
    {"title": "Vi börjar skolan igen",  # 5:54
     "tracks": ["0BUWJH8PENEkyEaX7FwJaE"]},
    {"title": "När vi klädde ut oss",  # 4:02
     "tracks": ["2NcnBm64hkWR0zed65qay9"]},
    {"title": "Det stora ovädret",  # 5:43
     "tracks": ["17zTaq2O6N7o9TxAH8DTUa"]},
    {"title": "Snart blir det jul",  # 5:29
     "tracks": ["3UJJ5f4c7UN5Q72k9fv8oR"]},
    {"title": "Hur vi firar jul i Bullerbyn",  # 10:21
     "tracks": ["0jQNBGivGQ2mFc1mZGuoYp"]},
    {"title": "Vi åker kälke",  # 3:57
     "tracks": ["0PxrrWhk0h1RMzUIX0tPlw"]},
    {"title": "Vi håller nyårsvaka",  # 6:59
     "tracks": ["3yGNSn7A4nTSjyEx5fwjBb"]},
    {"title": "Vi far på kalas till moster Jenny",  # 5:24
     "tracks": ["6WMGmwKTKuIFdPJsUZmQrW"]},
    {"title": "Lasse trillar i sjön",  # 4:43
     "tracks": ["1iztpAHwvxMTpbqL7kWLmL"]},
    {"title": "Anna och jag går och handlar",  # 7:42
     "tracks": ["7bnNBd5ytEcQ8polVPGxOZ"]},
    {"title": "Vi går i skolan och skojar med fröken",  # 7:13
     "tracks": ["2skMJxqPnfeZ4XZgKHVJeh"]},
    {"title": "Påsk i Bullerbyn",  # 6:52
     "tracks": ["0YbDCI69kFk0CDM5Lw7KiH"]},
    {"title": "Vi tittar på näcken",  # 10:25
     "tracks": ["1ks9SLLl8B9ZioiVKcUqJe"]},
    {"title": "Olle får en syster",  # 8:28
     "tracks": ["6WhzbFTo3K57UTntjZXpJN"]},
    {"title": "När det regnar",  # 8:46
     "tracks": ["2TZZEwRPaRhhi4bsGylYaD"]},
    {"title": "Vi letar efter skatten",  # 8:20
     "tracks": ["4j2O0R29XC5chSb3MpvR1q"]},
    {"title": "Anna och jag gör folk glada",  # 9:47
     "tracks": ["2krVh6jCo1deBlhbleZEw5"]},
    {"title": "Farfar fyller 80 år",  # 4:22
     "tracks": ["7b7cuOWhLWgNRtfeWISBe7"]},
    {"title": "Jag får en lammunge",  # 7:41
     "tracks": ["711UJEDB13vf8ij3g0Tily"]},
    {"title": "Pontus går i skolan",  # 7:56
     "tracks": ["6bUFpAmrUG2W0GkkevRI20"]},
    {"title": "När vi går hem från skolan",  # 11:27
     "tracks": ["5Bh3et70l9NoKulTVnPIwA"]},
    {"title": "Olle har en lös tand",  # 9:13
     "tracks": ["43mZsIwuqGHvrAzy0hvxVV"]},
    {"title": "Anna och jag vet inte själva vad vi gör",  # 5:49
     "tracks": ["4yhPscgUxpjYtstvc3vZsG"]},
    {"title": "De vises skrin",  # 12:44
     "tracks": ["6asnobJzBA4W1MZfCDPB0Q"]},
    {"title": "Lasse fångar uroxar",  # 12:47
     "tracks": ["5x7JP6WpeOViAUR0NjdLCM"]},
    {"title": "Körsbärsbolaget",  # 13:17
     "tracks": ["3QXHmavDZWRC74HDXfRZ9r"]},
    {"title": "Anna och jag tänker bli barnsköterskor - kanske",  # 13:35
     "tracks": ["2QIcEYw3WZE9B0owlFaRfe"]},
    {"title": "Vi fiskar kräftor",  # 12:40
     "tracks": ["3QyTGEi79VREzVZg79J9UR"]},
    # Julberättelser - Astrid Lindgren läser och berättar (Del 1-2)
    {"title": "Vi har så roligt när det är jul",  # 10:28
     "tracks": ["6HUGr82w3Mrh53gQImkbCp", "07cuI7UZT3Tg3B66L8csgp"]},
    {"title": "Godnatt, Herr Luffare",  # 13:23
     "tracks": ["6akg5mNWMxkbN5rDA7GJra", "61mO23A9rVSpAdQu9R2Pyl", "4K1ZlvVbypicRY9ts5vJaj"]},
    {"title": "Jul i stallet",  # 4:10
     "tracks": ["4DKYHKhChONn72YECtQY2r"]},
    # Emil i Lönneberga
    {"title": "Hundragubbesjubileet",  # 10:24
     "tracks": ["2JUtU7pefe36iylTBbQL3S"]},
    {"title": "När Emil körde huvet i soppskålen",  # 5:57
     "tracks": ["0tnWl31mfcX0kvR2FRN33j"]},
    {"title": "När Emil hissade upp lilla Ida i flaggstången",  # 3:45
     "tracks": ["0Jb06RYVliJdYdcBeb3Una"]},
    {"title": "Stora tabberaset i Katthult",  # 12:26
     "tracks": ["4Vueq82C4QHgzdHpxTZs9C"]},
    # Nya hyss av Emil i Lönneberga
    {"title": "Nya hyss av Emil i Lönneberga",  # 6:21
     "tracks": ["23R4jhVhFudWJHBiSrwfuE"]},
    # Än lever Emil i Lönneberga
    {"title": "Än lever Emil i Lönneberga",  # 5:49
     "tracks": ["7uNIVHuc4zPX8ruAaikXJ4"]},
    {"title": "Diverse små dagar i Emils liv",  # 13:47
     "tracks": ["0K1tzZl4GCRmLlVLilbF1n", "6QJf0Pt40LVSLIJlElM18O", "3IMdhF1hj8hlJyoe55R0Sz"]},
    {"title": "När det var husförhör i Katthult och Emil spärrade in sin fader i Trisseboda",  # 16:50
     "tracks": ["6msBDm2xjm1f9BfhCaGmiM", "6VLGH8WTc0wkS1pN76VQvg", "7AwZtvL4IMseFni3MV25Cn"]},
    # Madicken
    {"title": "Rickard",  # 9:14
     "tracks": ["4rBTVJDL94hxKMSlbDbtSP", "2Mk7wueAPMEGv0OqpzSga5"]},
    # Madicken på Junibacken
    {"title": "Moses i vassen",  # 6:19
     "tracks": ["00aAekQrzlXKLGUyTLrFGT"]},
    {"title": "Ge mej mera köttbullar",  # 1:34
     "tracks": ["3heswHtaGB6mCgzda1gRwt"]},
    {"title": "Madicken flyger och far",  # 6:52
     "tracks": ["3ILbb6ZivVtlwnj7YmqRFI"]},
    {"title": "Kan vi inte betala så är det ajöss med byrån",  # 5:41
     "tracks": ["26HKItHs1HGq62nE6cbLjD"]},
    {"title": "Tant Nilsson får tillbaka sin kropp",  # 5:25
     "tracks": ["53MbQP4h9BvP9KfmIUXtya"]},
    {"title": "Junibackens jul",  # 9:09
     "tracks": ["05jcLKDlWQoIMZFBOBEqU6"]},
    {"title": "Den förskräcklige Rickard",  # 5:38
     "tracks": ["6B9nKrbnwD39GMWqbIOVP3"]},
    {"title": "Lisabet pillar in en ärta i näsan",  # 8:06
     "tracks": ["6XwRMCl2baHLKqAxeGfZB3"]},
    # Du är inte klok Madicken
    {"title": "Madicken går till majelden i nya sandaler",  # 12:09
     "tracks": ["26MvaEzYS3UxiaozpB3DlD"]},
    {"title": "Finns det nån dummare unge än Mia?",  # 10:14
     "tracks": ["0N3gWZVYdWfi5sFSDRrwVA"]},
    {"title": "Mia bjuder på chokladpraliner",  # 8:32
     "tracks": ["5SBaiERE6SHUxvcj0LimAf"]},
    {"title": "Examen",  # 1:18
     "tracks": ["5W1qdSXZIETurESdRW7X0z"]},
    {"title": "Den stora avlusningen",  # 7:36
     "tracks": ["0hQRD9fXu6y0VjlX6tVKu0"]},
    {"title": "Där rök den julaftonen",  # 4:58
     "tracks": ["0RceKSPyjXQAowECFu7Vq3"]},
    # Lillebror och Karlsson på taket
    {"title": "Karlsson på taket",  # 13:40
     "tracks": ["6rPP0dPt88znRT0p1PZQvB", "4lSl6oER9Et8eNafHZ65y9", "56vtDzoARAVo9fC5HpZYWW"]},
    {"title": "Karlsson bygger torn",  # 14:24
     "tracks": ["3PxvPHqjnlo9nsHH7kkzyO", "0ppEMucRC4Js6lOQFYWlK3", "4v8prjcSd5TwfDlI0fOm61"]},
    {"title": "Karlsson leker tält",  # 16:38
     "tracks": ["15BGkJO8nTbSE9G8LEiz9s", "4yahAHv3wRLjLkx4HCWY5s", "6ZTQVG6wK4AGTzmse9b8Iy", "3ouvUB1hiYkkMASyKrZgzO"]},
    # Lotta på Bråkmakargatan
    {"title": "Alla är så elaka mot Lotta",  # 9:01
     "tracks": ["6AygQIsGQ6G0kgwXIfoUPy", "5m9JT8FJceGETETRJAbegG"]},
    {"title": "Lotta flyttar hemifrån",  # 2:36
     "tracks": ["6CwlKPARaKd8EyqIZNiEKR"]},
    {"title": "Vart ska Lotta ta vägen?",  # 12:10
     "tracks": ["2Sz7n5kdAoOWrVdkhaBoVW", "3KOMJVUm9avwiBry8JuKKJ", "4NP97le5JRHfXy2b5M8isk"]},
    {"title": "Lotta får besök",  # 3:59
     "tracks": ["4iqGIVvpB77WPJkW0PmAR7"]},
    {"title": "Då är jag ensam om natten...",  # 6:33
     "tracks": ["0eMhgfaukSfc1Xdl8FFfm4", "4bI2wOfYCiGlX4O8MQQzHE"]},
    {"title": "Visst kan Lotta cykla",  # 17:59
     "tracks": ["1WQXdhdYzwm0sYXHkhaqkf", "1S1eVfaxn3zG39fhuRWFUb", "2SPwPeCGi2zzYXq9uSI808", "7gjJ2ssHJWUHVNTtUyUOWA"]},
    # Barnen på Bråkmakargatan
    {"title": "Lotta är så barnslig",  # 5:38
     "tracks": ["357HnkRp3uVvv1NQT0P63a"]},
    {"title": "Vi leker hela dagarna",  # 4:53
     "tracks": ["3UlLn0iDIVcor4PiUMkQqC"]},
    {"title": "Lotta är envis som en gammal get",  # 5:11
     "tracks": ["3BXPqo4J0m04ajLnqg6lGC"]},
    {"title": "Tant Berg är den snällaste som finns",  # 6:52
     "tracks": ["1s8bjvrsEEod6Y7pwVb4df", "49dnSoBa7AfKK0h0Z3jEJu"]},
    {"title": "Vi gör en utflykt",  # 9:25
     "tracks": ["24TccKuLTdnSYK0rT7zUus", "2DHKasHqISRbK4RnR2Rtpk"]},
    {"title": "Vi far till mormor och morfar",  # 6:02
     "tracks": ["1bHl3X4ptNcfzieMayQAZs", "4dfd52ZkwoWuOypmrD0qff"]},
    {"title": "Lotta säger närapå svärord",  # 7:59
     "tracks": ["2Dbs8NoYAqZc6jXENZXudD", "4wyuSXksEVaBE0bR3Eg5V4"]},
    {"title": "Lotta har onixdag",  # 6:01
     "tracks": ["6ITd0v0jvdJaSgzk2ov7Ka", "3lLPpiSp6tstTWEaZnT7Wg"]},
    # Lotta flyttar hemifrån
    {"title": "Vi går till tandläkaren",  # 2:38
     "tracks": ["1IjedFeh06QJRzjqLU7dfn"]},
    {"title": "Lotta kan nästan allting faktiskt",  # 8:17
     "tracks": ["0eGhvLaVrnsVqPwmLPmbnX"]},
    # Här kommer Pippi Långstrump
    {"title": "Pippi flyttar in i Villa Villekulla",  # 3:49
     "tracks": ["0W6YmdA7vRCtB7eWB3bYMq"]},
    {"title": "Pippi, Prysselius och poliserna",  # 4:15
     "tracks": ["6eZdLSpu12ltX9bTUfTXK6"]},
    {"title": "Pippi är sakletare",  # 2:15
     "tracks": ["7KcFuZYPgIjLSafoYfwXy0"]},
    {"title": "Pippi skurar golv",  # 3:03
     "tracks": ["6exDaz6mGb5Zs8hxE7TuaI"]},
    {"title": "Pippi går i skolan",  # 4:12
     "tracks": ["0WR8hgLgPknzOdsAyOAr5N"]},
    {"title": "Pippis födelsedag",  # 3:28
     "tracks": ["5w8KWT4eG0xwe5X1ivT7aW"]},
    {"title": "Pippi får besök av tjuvar",  # 2:47
     "tracks": ["5IoSZKsuHQleC4QN2ntIxs"]},
    {"title": "Pippis jul",  # 2:43
     "tracks": ["5mUUgo909mnbln2AxDzCLf"]},
    {"title": "Pippi på en öde ö",  # 2:29
     "tracks": ["5NEoLSbJSii3TJKj94MlNl"]},
    {"title": "Pippis avskedskalas",  # 4:15
     "tracks": ["4tBSTDmvyic1TW8i8PZUci"]},
    {"title": "Pippi går ombord",  # 6:46
     "tracks": ["5RkHS96jfZh0sppqYErEyQ"]},
    # Kajsa Kavat hjälper mormor
    {"title": "Kajsa Kavat hjälper mormor",  # 14:20
     "tracks": ["3S04U7NzQhZMF3bJFJDSOy"]},
    # Nils Karlsson Pysslings bästa
    {"title": "Nils Karlsson-Pyssling",  # 20:23
     "tracks": ["2EL3rh1FoMUJvCLIVzEssz", "4tWLwuQBI3qN3vlM3e8ZsU", "5DucoAqMqQdCUhJv3RZBAh", "4WYvtcgQWPdr9bZYp93dOp"]},
    {"title": "Nils Karlsson-Pyssling flyttar in",  # 20:22
     "tracks": ["3lyZW2N7J1fpCjx1KFmKQu", "1Qz9zgN8E6Zzl2QScGIo6h", "4555C6DlR3n1AFNM79YBkc", "33Ox2pkYzmkecCB0w6tTP9"]},
    # Peter och Petra
    {"title": "Peter och Petra",  # 11:01
     "tracks": ["1hyywsj23KmjQqNicI7Qe8", "2dSiHDDw7Qb7FcPipTP1Qf"]},
    # Allra käraste syster
    {"title": "Allra käraste syster",  # 9:36
     "tracks": ["0LvZ0cMHknb9lbed7CrdV7", "7FWojeZGLg7U0FlWWyneOF"]},
    # En natt i maj
    {"title": "En natt i maj",  # 10:55
     "tracks": ["241ua0MZtVCh2zMdYyKSpx", "7tLy7hteNHDEuuy3w2ivNs"]},
    # I Skymningslandet
    {"title": "I Skymningslandet",  # 15:17
     "tracks": ["4deCpRqkLAiKwWx87JyFvD", "6hZ0IzzsplSD9crfe4IGeW", "33Sn7SEGpQy9rm15jz2MuZ"]},
]
