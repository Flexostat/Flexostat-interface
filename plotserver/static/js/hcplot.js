//some constants:
basedataurl = '/log.dat';
reloadPeriod = 2; //min

//some globals:
tf = 0;
odchart = null;
uchart = null;

$(function(){
  // Set some API options
  // Don't use utc, use local time.
  Highcharts.setOptions({
    global: {
        useUTC: false
    }
  });

  var reloadPeriodMS = reloadPeriod * 60.0 * 1000.0;
  setInterval(loadPlots, reloadPeriodMS);
  loadPlots();
});

// TODO: only load recent data
function loadPlots(){
  var req = jQuery.ajax(
              basedataurl,
              {dataType:'text'});
  req.done(function(data){
    var lines = data.replace(/[\[\], ]+/g," ").trim().split("\n");
    //parse lines into 2d array of numbers.
    var nd = [];
    for (ind in lines) {
      var line = lines[ind];
      nd[ind] = jQuery.map(line.trim().split(' '),
                           function(v,k){return Number(v);});
    }
    odchart = makeplot('odplot', getSeries(nd,'OD'));
    odchart.setTitle({text: "Optical Density"});
    uchart = makeplot('uplot', getSeries(nd,'U'));
    uchart.setTitle({text: "Dilution Rate"});
  });
}


function getSeries(numData, datatype){
  /*numData: the numerical array of raw data
   *datatype: 'OD': the optical density data, 'U': the dilution rate data.
   */
  if (datatype === "OD") {
    var offset = 1;
  } else if (datatype === "U") {
    var offset = 9;
  } else {
    return null;
  }
  var seriesData = [];
  var t0 = numData[0][0];
  for (ind in numData){
    var datum = [];
    var d = numData[ind];
    for (var odind = 0; odind<8;odind++){
      datum[odind] = ([d[0]*1000,d[odind+offset]]); //[time,OD]
    }
    seriesData[ind] = datum;
  }
  return seriesData;
}

function makeplot(thediv, seriesdata) {
  /*thediv: string name of div id to plot to
   *seriesdata: the series data:
   *  seriesdata[j]: the data corresponding to the j th time point
   *    seriesdata[j][k]: the data point: [time,value]
   *
   *returns: a chart object so data can be appended later.
   */

  //transpose
  //init arrays
  hcdata = [];
  for (ii =0;ii<seriesdata[0].length;ii++) {
    hcdata[ii]=[];
  }

  //fill hcdata as in [[series1], [series2], ...]
  for (rowind in seriesdata) {
    row = seriesdata[rowind];
    for (datumind in row) {
      datum = row[datumind];
      hcdata[datumind][rowind] = datum;
    }
  }

  //pack into hc array.
  var hcseries = [];
  for (ind in hcdata) {
    hcdata[ind] = {data:hcdata[ind],
                   name:'Chamber '+(Number(ind)+1),
                   tooltip: {
					           valueDecimals: 4
                   }};
  }

  var divName = '#' + thediv;
  var myDiv = $(divName);
  var myChart = myDiv.highcharts();
  myDiv.highcharts('StockChart', {
    chart: {renderTo: thediv},
    series: hcdata,
    legend: {enabled: true},
    rangeSelector: {
      buttons: [{type:'minute', count: 60, text: '1hr'},
                {type:'minute', count: 60*3, text: '3hr'},
                {type:'minute', count: 60*12, text: '12hr'},
                {type:'day', count:1, text: '1d'},
                {type:'day', count:3, text: '3d'},
                {type:'week', count:1, text: '1wk'},
                {type:'all', text:'All'}]
    },
  });

  return $(divName).highcharts();
}