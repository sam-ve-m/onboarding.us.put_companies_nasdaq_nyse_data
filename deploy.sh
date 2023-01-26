fission spec init
fission env create --spec --name onb-us-cmpn-drct-env --image nexus.sigame.com.br/fission-onboarding-us-company-director-ben:0.1.0 --poolsize 2 --graceperiod 3 --version 3 --imagepullsecret "nexus-v3" --spec
fission fn create --spec --name onb-us-cmpn-drct-fn --env onb-us-cmpn-drct-env --code fission.py --executortype poolmgr --requestsperpod 10000 --spec
fission route create --spec --name onb-us-cmpn-drct-rt --method PUT --url /onboarding/company_director_us --function onb-us-cmpn-drct-fn