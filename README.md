# Проблема с временными зонами (а как же без этого...)

В PostgreSQL все DateTime объекты переводятся в локальную временную зону, из-за этого всё входящее время, выходит немного другим. На сервере я выставил временную зону UTC, и данное ограничение PostgreSQL обойти не получилось, прошу учесть это при тестировании