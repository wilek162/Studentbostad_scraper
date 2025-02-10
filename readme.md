# Studentbostad Scraper

## Beskrivning

Detta projekt är designat för att hjälpa studenter att hålla koll på nya lägenhetsannonser på den svenska hemsidan [studentbostader.se](https://www.studentbostader.se). Webbplatsen uppdateras ofta med tillgängliga studentbostäder, där principen "först till kvarn" gäller.

Denna scraper automatiserar processen att kontrollera när nya annonser läggs upp och skickar e-postmeddelanden för att ge användaren större chans att ansöka om dessa lägenheter så snart de är tillgängliga.

## Hur det fungerar

1. Scrapern besöker [studentbostader.se](https://www.studentbostader.se) och hämtar det aktuella antalet tillgängliga lägenheter.
2. Om antalet lägenheter har förändrats skickas ett e-postmeddelande med den uppdaterade informationen och en länk till sidan.
3. Scrapern körs automatiskt var 24:e timme för att säkerställa att användaren alltid är uppdaterad med de senaste annonserna.
