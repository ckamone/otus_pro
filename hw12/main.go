package main

import (
	"./appinstalled"
	"bufio"
	"compress/gzip"
	"errors"
	"flag"
	"fmt"
	"github.com/bradfitz/gomemcache/memcache"
	"github.com/golang/protobuf/proto"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"
)

type AppInstalled struct {
	devType string
	devId   string
	lat     float64
	lon     float64
	apps    []uint32
}

type Opts struct {
	test    bool
	dry     bool
	pattern string
	idfa    string
	gaid    string
	adid    string
	dvid    string
}

//Rename loaded file
func dotRename(path string) {
	newFilename := "." + filepath.Base(path)
	newPath := filepath.Join(filepath.Dir(path), newFilename)
	os.Rename(path, newPath)
}

//Upload data in Memcache
func insertAppsinstalled(memcClient *memcache.Client, appsinstalled *AppInstalled, dryRun bool) bool {
	key := appsinstalled.devType + ":" + appsinstalled.devId
	ua := msg.UserApps{}
	ua.Lat = &appsinstalled.lat
	ua.Lon = &appsinstalled.lon
	ua.Apps = appsinstalled.apps
	packed, err := proto.Marshal(&ua)
	if err != nil {
		log.Printf("marshaling error: %s", err)
		return false
	}
	if dryRun {
		log.Printf("%s -> %s\n", key, ua.Apps)
		return true
	} else {
		item := &memcache.Item{Key: key, Value: []byte(packed)}
		for i := 0; i < 5; i++ {
			if err := memcClient.Set(item); err == nil {
				return true
			}
			time.Sleep(2 * time.Second)
		}
	}
	return false

}

//Parse read string from file
func parseAppsinstalled(line string) (*AppInstalled, error) {
	lineParts := strings.Split(strings.TrimSpace(line), "\t")
	if len(lineParts) < 5 {
		return nil, errors.New("Error in format line\t")
	}
	devType := lineParts[0]
	devId := lineParts[1]
	if len(devType) == 0 || len(devId) == 0 {
		return nil, errors.New("Error in devType or devId\t")
	}
	lat, errLat := strconv.ParseFloat(lineParts[2], 64)
	lon, errLon := strconv.ParseFloat(lineParts[3], 64)
	if errLat != nil || errLon != nil {
		return nil, errors.New("Invalid geo coords\t")
	}

	var apps []uint32

	for _, app := range strings.Split(lineParts[4], ",") {
		num, err := strconv.ParseUint(app, 10, 32)
		if err != nil {
			log.Printf("Not all user apps are digits: %s", line)
		} else {
			apps = append(apps, uint32(num))
		}
	}

	return &AppInstalled{
		devId:   devId,
		devType: devType,
		lat:     lat,
		lon:     lon,
		apps:    apps,
	}, nil
}

//Handle file
func fileHandler(filePath string, memcClients map[string]*memcache.Client, NormalErrRate float64, dry bool, wg *sync.WaitGroup) {
	defer wg.Done()
	defer dotRename(filePath)
	var processed, errors int
	fd, err := os.Open(filePath)
	if err != nil {
		log.Println(err)
		return
	}
	defer fd.Close()
	extData, err := gzip.NewReader(fd)
	if err != nil {
		log.Println(err)
		return
	}
	defer extData.Close()
	scan := bufio.NewScanner(extData)

	for scan.Scan() {
		appinstalled, err := parseAppsinstalled(scan.Text())
		if err != nil {
			log.Println(err)
			errors += 1
			continue
		}
		if memcClient, ok := memcClients[appinstalled.devType]; ok {
			result := insertAppsinstalled(memcClient, appinstalled, dry)
			if result {
				processed += 1
			} else {
				errors += 1
			}
		} else {
			errors += 1
			log.Printf("Unknow device type: %s", appinstalled.devType)
		}
	}
	if processed != 0 {
		errRate := float64(errors) / float64(processed)
		if errRate < NormalErrRate {
			log.Printf("Acceptable error rate (%.2f). Successfull load", errRate)
		} else {
			log.Printf("High error rate (%.2f > %.2f). Failed load", errRate, NormalErrRate)
		}
	}

}

//Read console params
func consoleRead() Opts {
	opts := Opts{}
	flag.BoolVar(&opts.test, "t", false, "test mode")
	flag.BoolVar(&opts.dry, "dry", false, "run in debug mode")
	flag.StringVar(&opts.pattern, "pattern", "./data/[^.]*.tsv.gz", "log path pattern")
	flag.StringVar(&opts.idfa, "idfa", "127.0.0.1:33013", "idfa server address")
	flag.StringVar(&opts.gaid, "gaid", "127.0.0.1:33014", "gaid server address")
	flag.StringVar(&opts.adid, "adid", "127.0.0.1:33015", "adid server address")
	flag.StringVar(&opts.dvid, "dvid", "127.0.0.1:33016", "dvid server address")
	flag.Parse()
	return opts
}

//run Memcache clients
func runMemcacheClients(deviceAdr map[string]string) map[string]*memcache.Client {
	clients := map[string]*memcache.Client{}
	for key, address := range deviceAdr {
		newClient := memcache.New(address)
		clients[key] = newClient
	}
	return clients
}

func main() {
	startTime := time.Now()
	var wg sync.WaitGroup
	opts := consoleRead()
	deviceMemc := map[string]string{
		"idfa": opts.idfa,
		"gaid": opts.gaid,
		"adid": opts.adid,
		"dvid": opts.dvid,
	}
	files, _ := filepath.Glob(opts.pattern)
	clients := runMemcacheClients(deviceMemc)

	for _, file := range files {
		wg.Add(1)
		go fileHandler(file, clients, 0.1, opts.dry, &wg)
	}
	wg.Wait()
	fmt.Printf("Elapsed time: %v", time.Since(startTime))
}
