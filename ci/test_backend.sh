#!/bin/bash
export COMPOSE_PROJECT_NAME=twitter-tranquilo_${CI_COMMIT_SHA}
docker-compose -f docker/compose/test.yml run twitter-tranquilo unittests.sh
exitcode=$?
docker-compose -f docker/compose/test.yml down
exit $exitcode
