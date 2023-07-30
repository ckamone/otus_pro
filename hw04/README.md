# otus_pro_04

## start sever
python3 httpd.py
python3 httpd.py -p 8080 -w 20

## get
curl -v http://localhost:8080/

## head
curl -v --head http://localhost:8080/

## post
curl --request POST --data '{"username":"xyz","password":"xyz"}' http://localhost:8080/

## test
python3 httptest.py

## browser test
http://localhost/httptest/wikipedia_russia.html 

## load test 
ab -n 50000 -c 100 -r http://localhost:8080/ 

## load test result @20 workers
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        Microsoft-IIS/6.0
Server Hostname:        localhost
Server Port:            8081

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   20.303 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      5850000 bytes
HTML transferred:       0 bytes
Requests per second:    2462.68 [#/sec] (mean)
Time per request:       40.606 [ms] (mean)
Time per request:       0.406 [ms] (mean, across all concurrent requests)
Transfer rate:          281.38 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       2
Processing:     0   41  12.3     40     118
Waiting:        0   40  12.2     40     118
Total:          1   41  12.3     41     118

Percentage of the requests served within a certain time (ms)
  50%     41
  66%     44
  75%     46
  80%     48
  90%     53
  95%     61
  98%     71
  99%     84
 100%    118 (longest request)