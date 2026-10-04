.PHONY: run run-local offline-eval test eval offline-check triage-seed stop

run:
	$(MAKE) -C track_2b run

run-local:
	$(MAKE) -C track_2b run-local

offline-eval:
	$(MAKE) -C track_2b offline-eval

test:
	$(MAKE) -C track_2b test

eval:
	$(MAKE) -C track_2b eval

offline-check:
	$(MAKE) -C track_2b offline-check

triage-seed:
	$(MAKE) -C track_2b triage-seed

stop:
	$(MAKE) -C track_2b stop
