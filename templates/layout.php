<?php
if(!isset($_COOKIE["color"]))
{
    setcookie("color", "red");
}
?>

<!DOCTYPE html>

<html lang="en">

    <head>

        <meta charset="utf-8">
        <meta name="viewport" content="initial-scale=1, width=device-width">

        <!-- http://getbootstrap.com/docs/5.1/ -->
        <link crossorigin="anonymous" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" rel="stylesheet">
        <script crossorigin="anonymous" src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"></script>

        <!-- https://favicon.io/emoji-favicons/weary-cat -->
        <link href="/static/favicon.ico" rel="icon">

        <link href="/static/main.css" rel="stylesheet">

        <!-- Colours -->
        <link class="general_colors" id="red" href="/static/red.css" rel="stylesheet" disabled>
        <link class="general_colors" id="orange" href="/static/orange.css" rel="stylesheet" disabled>
        <link class="general_colors" id="yellow" href="/static/yellow.css" rel="stylesheet" disabled>
        <link class="general_colors" id="lime_green" href="/static/lime_green.css" rel="stylesheet" disabled>
        <link class="general_colors" id="green" href="/static/green.css" rel="stylesheet" disabled>
        <link class="general_colors" id="turquoise" href="/static/turquoise.css" rel="stylesheet" disabled>
        <link class="general_colors" id="blue" href="/static/blue.css" rel="stylesheet" disabled>
        <link class="general_colors" id="blue_purple" href="/static/blue_purple.css" rel="stylesheet" disabled>
        <link class="general_colors" id="purple" href="/static/purple.css" rel="stylesheet" disabled>
        <link class="general_colors" id="pink" href="/static/pink.css" rel="stylesheet" disabled>

        <!--TESTING-->
        <?php
        if($_COOKIE["color"] != "")
        {
            echo $_COOKIE["color"];
        }
        ?>


        <script>
            document.addEventListener('DOMContentLoaded', function(){
                if (localStorage.general_color)
                {
                    document.getElementById(localStorage.general_color).disabled = false
                }
                else
                {
                    localStorage.setItem("general_color", "red")
                    document.getElementById(localStorage.general_color).disabled = false
                }
            })
        </script>

        <title>MY Planner: {% block title %}{% endblock %}</title>

    </head>

    <body>

        <nav class="bg-light border navbar navbar-expand-md navbar-light" >
            <div class="container-fluid">
                <a class="navbar-brand" href="/"><span>MY</span> <span class="cursive color pastelred">Planner</span></a>
                <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-bs-target="#navbar" data-bs-toggle="collapse" type="button">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar">
                    {% if session["user_id"] %}
                        <ul class="navbar-nav me-auto mt-2">
                            <li class="nav-item"><a class="nav-link" href="/calendar">Calendar</a></li>
                            <li class="nav-item"><a class="nav-link" href="/fixed">Regular</a></li>
                            <li class="nav-item"><a class="nav-link" href="/events">Events</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto mt-2">
                            <li class="nav-item"><a class="nav-link" href="/settings">Settings</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logout">Log Out</a></li>
                        </ul>
                    {% else %}
                        <ul class="navbar-nav ms-auto mt-2">
                            <li class="nav-item"><a class="nav-link" href="/register">Register</a></li>
                            <li class="nav-item"><a class="nav-link" href="/login">Log In</a></li>
                        </ul>
                    {% endif %}
                </div>
            </div>
        </nav>

        {% if get_flashed_messages() %}
            <header>
                <div class="alert alert-primary mb-0 text-center" role="alert">
                    {{ get_flashed_messages() | join(" ") }}
                </div>
            </header>
        {% endif %}

        <main class="container-fluid py-5 text-center">
            {% block main %}{% endblock %}
        </main>

        <footer class="mb-5 small text-center text-muted">
            Created by Andrea Tan
        </footer>

    </body>

</html>
