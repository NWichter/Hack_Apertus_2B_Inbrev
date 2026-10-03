.PHONY: run test eval offline-check stop

run:
	$(MAKE) -C track_2b run

test:
	$(MAKE) -C track_2b test

eval:
	$(MAKE) -C track_2b eval

offline-check:
	$(MAKE) -C track_2b offline-check

stop:
	$(MAKE) -C track_2b stop
