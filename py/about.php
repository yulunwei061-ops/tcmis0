<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>魏郁倫簡介</title>

    <style type="text/css">
        * { 
            font-family: "標楷體"; 
            margin-left: auto; 
            margin-right: auto; 
        }
        h1 { 
            color: blue; 
            font-size: 60px; 
        }
        h2 { 
            color: #33ff33; 
            font-size: 40px; 
        }
    </style>

    <script>
        function change1() {
            
            document.getElementById("pic").src = "mountain.jpg";
            document.getElementById("h2text").innerText = "靜宜資管";
        }

        function change2() {
            
            document.getElementById("pic").src = "cliff.jpg";
            document.getElementById("h2text").innerText = "Yu-Lun Wei";
        }
    </script>
</head>
<body>

    <center>
        <table width="80%" border="0">
            <tr>
                <td width="70%">
                    <img src="cliff.jpg" width="100%" id="pic" 
                         onmouseover="change1()" 
                         onmouseout="change2()">
                </td>
                <td valign="middle" align="center">
                    <h1>魏郁倫</h1>
                    <h2 id="h2text">Yu-Lun Wei</h2>
                </td>
            </tr>
        </table>

        <br>

        <table width="80%" border="1">
            <tr>
                <td valign="top" align="left">
                    個人網頁：<a href="https://www.pu.edu.tw/">https://www.pu.edu.tw/</a><br>
                    FB：<a href="https://zh-tw.facebook.com/wei.yu.lun.8498" target="_blank">https://zh-tw.facebook.com/wei.yu.lun.8498</a><br>
                    Tel：<a href="tel:0988772348">0988772348</a><br>
                    E-Mail：<a href="mailto:yulunwei061@gmail.com">yulunwei061@gmail.com</a><br>
                </td>

                <td valign="top">
                    大象席地而坐電影配樂<br>
                    <audio controls>
                        <source src="elephant.mp3" type="audio/mp3">
                    </audio>
                </td>

                <td valign="top">
                    不要去臺灣<br>
                    <iframe src="https://www.youtube.com/embed/pW88QFpHXa8" allowfullscreen width="300" height="150"></iframe>
                </td>
            </tr>
        </table>
    </center>

</body>
</html>