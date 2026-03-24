# Datagrundlag

Filen [data/folketing_partier_over_tid.csv](data/folketing_partier_over_tid.csv) viser en afledt serie for folketingsvalg over tid:

- `election_date`: valgdato
- `next_election_date`: datoen for det efterfoelgende valg
- `parties_in_folketing`: antal partier med mindst eet mandat efter valget
- `days_to_next_election`: antal kalenderdage til det efterfoelgende valg
- `note`: kort note, hvor der er en afgraensning eller saerlig haendelse

## Afgraensning

Serien er lavet til analyse paa valgniveau, ikke paa mellemliggende aendringer i folketingsgruppen mellem valg. Tallet `parties_in_folketing` er derfor opgjort som:

`antal partier med mindst eet mandat efter folketingsvalget`

Til sammenlignelighed er kandidater uden for partierne ikke talt med i partitallet.

## Note om 1994

Ved folketingsvalget den 21. september 1994 blev Jacob Haugaard valgt uden for partierne. I CSV-filen er 1994 derfor registreret som `8` partier, og Jacob Haugaard er omtalt i note-kolonnen, men ikke medregnet som parti.

## Kilde

Dataserien er sammenstillet med Danmarks Statistik som kilde:

- Danmarks Statistik, temaet *Folketingsvalg*: https://www.dst.dk/da/Statistik/emner/borgere/demokrati/folketingsvalg
- Danmarks Statistik, *Statistisk Årbog 1961*, afsnittet *Offentlige valg*: https://www.dst.dk/pubfile/13352/offvalg
- Danmarks Statistik, *Statistisk Årbog 1970*, afsnittet *Offentlige valg*: https://www.dst.dk/pubfile/13349/offvalg

De nyere valg er afledt fra Danmarks Statistiks valgoversigter, og de historiske valg er afledt fra de offentligt tilgaengelige aargangs-/publikationsoversigter hos Danmarks Statistik.
