<?php include "functions.php"; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <?= style_script() ?>
    <title>Login</title>
</head>
<body class="text-center">
    <?php
    $notif = null;
    if (isset($_POST['username']) && isset($_POST['password'])) {

        session_start();
        $user = $_POST['username'];
        $pass = $_POST['password'];
        $salt = "XDrBmrW9g2fb";
        $pdo = pdo_connect();
        $stmt = $pdo->prepare('SELECT * FROM users WHERE username = "' . $user . '" AND password = "' . $pass . '" LIMIT 1');
        $stmt->execute();
        $notif = $stmt->rowCount();
        if ($stmt->rowCount() > 0) {
            $_SESSION['user'] = $user;
            header("location: index.php");
        } else {
            $notif = "Damn, wrong credentials!!";
        }
    }

    ?>
    <form class="form-signin" method="POST">
        <h1 class="h3 mb-3 font-weight-normal">Damn, sign in!</h1>
        <label for="inputUsername" class="sr-only">Username</label>
        <input type="username" id="inputUsername" name="username" class="form-control" placeholder="Username" required autofocus>
        <br>
        <label for="inputPassword" class="sr-only">Password</label>
        <input type="password" id="inputPassword" name="password" class="form-control" placeholder="Password" required>
        <div class="checkbox mb-3">
            <label>
                <?= $notif ?>
            </label>
        </div>
        <button class="btn btn-lg btn-danger btn-block" type="submit">OK I'm sign in</button>
        <p class="mt-5 mb-3 text-muted">Your Damn Exercise &copy; 2023</p>
    </form>
</body>

</html>
