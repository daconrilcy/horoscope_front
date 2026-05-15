# Reference runtime after

## Commandes
- alembic upgrade head
- sqlite3 horoscope.db ".schema astral_aspect_families"
- sqlite3 horoscope.db "SELECT COUNT(*) FROM astral_aspect_families;"
- sqlite3 horoscope.db "SELECT COUNT(*) FROM astral_aspects a JOIN astral_aspect_families f ON f.id = a.family;"
- sqlite3 horoscope.db "SELECT COUNT(*) FROM astral_aspects a LEFT JOIN astral_aspect_families f ON f.id = a.family WHERE f.id IS NULL;"
- sqlite3 horoscope.db "PRAGMA foreign_key_check;"
- python payload ReferenceDataService.get_active_reference_data('1.0.0')

## Sorties
Schema:
```sql
CREATE TABLE astral_aspect_families (
	id INTEGER NOT NULL, 
	name VARCHAR(32) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
```
Familles: 3
Aspects joints: 20
References invalides: 0
Foreign key check: 
Payload aspects: 20
