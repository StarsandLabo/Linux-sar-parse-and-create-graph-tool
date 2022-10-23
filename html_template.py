from random import randint

lineColors = (
  'rgb(229, 57, 53)', #red
  #'rgb(216, 27, 96)', #Pink
  'rgb(142, 36, 170)', #purple
  #'rgb(94, 53, 177)', #deep purple
  #'rgb(57, 73, 171)', #indigo
  'rgb(30, 136, 229)', #blue
  #'rgb(3, 155, 229)', #Light Blue
  'rgb(0, 172, 193)', #Cyan
  #'rgb(0, 137, 123)', #Teal
  'rgb(67, 160, 71)', #Grean
  #'rgb(124, 179, 66)', #Light Green
  'rgb(192, 202, 51)', #Lime
  'rgb(253, 216, 53)', #Yellow
  #'rgb(255, 179, 0)', #Amber
  'rgb(251, 140, 0)', #Orange
  #'rgb(244, 81, 30)', #DeepOrange
  'rgb(109, 76, 65)', #Brown
  'rgb(84, 110, 122)' #BlueGrey
)

def GetLineColorsRandom():
  return lineColors[randint(0, lineColors.__len__() - 1)]

class Dataset():
  def __init__(self) -> None:
    self.label = ''
    self.pointRadius = 0
    self.borderColor = GetLineColorsRandom()
    self.data = []
    
  def CreateDataset(self):
    return {
      "label": self.label,
      "pointRadius": self.pointRadius,
      "borderColor": self.borderColor,
      "data": self.data
    }

BASE_HTML="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<title>!!!title!!!</title>
</head><body>
!!!ChartPlaceholder!!!
</body></html>"""
CHART_PART="""<style>
#ex_chart {max-width:1280px;max-height:960px;}
</style>
<canvas id="chart"></canvas>
<img id="converted_img" src="" />
<details><summary>ProcessNames & Commandlines</summary>
<pre>
!!!processnames!!!
</pre>
</details>
<br />
<a hidden id="converted_imglink" href="">Chart image</a>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
  const labels = !!!labels!!! ;
  
  const data   = {
    labels: labels,
    datasets: !!!datasets!!!
  };
  const config = {
    type: 'line',
    data: data,
    options: {
      animation: false,
      plugins: {
        title: {
          display: true,
          position: 'bottom',
          font: { size: 20 },
          text: '!!!targetmetrics!!!'
        }
      },
      scales: {
        x: { 
          display: true,
          grid: {display: false}
        },
        y: {
          display: true,
          min: 0
        }
      }
    }
  };
  </script>
  <script>
    const myChart = new Chart(
      document.getElementById('chart'),
      config
    );
    
    // 画像を別途表示する場合は以下と冒頭aタグのコメントアウトを外す。
    // var image = myChart.toBase64Image();
    // document.getElementById('converted_img').setAttribute('src', image);
    // document.getElementById('converted_imglink').setAttribute('href', image);
  </script>"""

FORM_PART="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<title>!!!title!!!</title>
</head><body>
  <form id="upload">
    <input type="file" id="top">
    <button>Upload</button>
  </form>
</body></html>
"""