function updateChart(theUrl) {
    async function jsonGet(theUrl)
    {
        let response = await fetch(theUrl);
        if (response.ok) {
            let json = await response.json();
            //let newDiv = document.createElement('div1');
            //document.body.append(newDiv);
            //document.getElementById('data').innerHTML = json;
	        //console.log(json)
            return json;
        } else {
            alert('Error HTTP: ' + response.status);
        }

    }     

    jsonGet(theUrl).then(json => {
        //const date = json.date
        //const tx = json.tx
        //const rx = json.rx
        //console.log(date)
	Highcharts.chart('plot',{
	    xAxis: {
                categories: json.date
	    },
	    series: [
	        {
		    name: 'tx',
		    data: json.tx
		},
		{
		    name: 'rx',
		    data: json.rx
		},
	    ]
	})
    })  
};