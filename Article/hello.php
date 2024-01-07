<?php
    date_default_timezone_set('Asia/Singpaore');
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>Page Title</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel='stylesheet' type='text/css' href='style.css'>
</head>
<body>
<?php
echo "<form>
    <input type="hidden" name="uid" value="Anonymous">
    <input type="hidden" name="date" value='".date('Y-m-d H:i:s')."'>
    <textarea name='message'></textarea></br>
    <button type='submit' name='submit'>Comment</button>
</form>";
?>
</body>
</html>