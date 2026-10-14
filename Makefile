.PHONY: run run-local offline-eval test stop

run:
	$(MAKE) -C track_2b run

run-local:
	$(MAKE) -C track_2b run-local

offline-eval:
	$(MAKE) -C track_2b offline-eval

test:
	$(MAKE) -C track_2b test

stop:
	$(MAKE) -C track_2b stop
