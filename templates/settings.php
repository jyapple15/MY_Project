{% extends "layout.html" %}

{% block title %}
    Settings
{% endblock %}

{% block main %}
    <script>
        document.addEventListener('DOMContentLoaded', function(){
            options_box = document.querySelector("#options_box")
            color_options = document.querySelectorAll(".color_options")

            // Set opacity for all
            options_box.addEventListener('mouseenter', function(){
                for (let j = 0; j < color_options.length; j++)
                {
                   color_options[j].classList.add("low_opacity")
                }
            })
            options_box.addEventListener('mouseleave', function(){
                for (let j = 0; j < color_options.length; j++)
                {
                   color_options[j].classList.remove("low_opacity")
                }
            })

            // When hover, change opacity + set localStorage
            for (let i = 0; i < color_options.length; i++)
            {
                color_options[i].addEventListener('mouseenter', function(){
                    color_options[i].classList.remove("low_opacity")
                })
                color_options[i].addEventListener('mouseleave', function(){
                    color_options[i].classList.add("low_opacity")
                })
                color_options[i].addEventListener('click', function(){
                    old_color = localStorage.general_color
                    localStorage.setItem("general_color", color_options[i].id)
                    document.getElementById(localStorage.general_color).disabled = false
                    if (old_color != localStorage.general_color)
                    {
                        document.getElementById(old_color).disabled = true
                    }
                })

                //TESTING
                color_options[i].addEventListener('click', function(){
                    document.cookie = `color=${color_options[i].id}`
                })
            }
        });
    </script>

    <table width="85%">
        <tr>
            <td style="min-width:80px">
                <b>Colours?</b>
            </td>
            <td>
                <div id="options_box" class="wrap">
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="red">
                            <tr>
                                <td class="color_squares" style="background-color: #fff0f0;"></td>
                                <td class="color_squares" style="background-color: #ffe9e9;"></td>
                                <td class="color_squares" style="background-color: #ffc9c9;"></td>
                                <td class="color_squares" style="background-color: #ff9999;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="orange">
                            <tr>
                                <td class="color_squares" style="background-color: #fff2e6;"></td>
                                <td class="color_squares" style="background-color: #ffe6cc;"></td>
                                <td class="color_squares" style="background-color: #ffbf80;"></td>
                                <td class="color_squares" style="background-color: #ff8000;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="yellow">
                            <tr>
                                <td class="color_squares" style="background-color: #ffffe6;"></td>
                                <td class="color_squares" style="background-color: #ffffb3;"></td>
                                <td class="color_squares" style="background-color: #ffff66;"></td>
                                <td class="color_squares" style="background-color: yellow;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="lime_green">
                            <tr>
                                <td class="color_squares" style="background-color: #e6ffe6;"></td>
                                <td class="color_squares" style="background-color: #b3ffb3;"></td>
                                <td class="color_squares" style="background-color: #80ff80;"></td>
                                <td class="color_squares" style="background-color: #00ff00;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="green">
                            <tr>
                                <td class="color_squares" style="background-color: #e6fff5;"></td>
                                <td class="color_squares" style="background-color: #b3ffe0;"></td>
                                <td class="color_squares" style="background-color: #66ffb3;"></td>
                                <td class="color_squares" style="background-color: #00ff99;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="turquoise">
                            <tr>
                                <td class="color_squares" style="background-color: LightCyan;"></td>
                                <td class="color_squares" style="background-color: #bff3f3;"></td>
                                <td class="color_squares" style="background-color: #88e2e2;"></td>
                                <td class="color_squares" style="background-color: Turquoise;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="blue">
                            <tr>
                                <td class="color_squares" style="background-color: #e6eaff;"></td>
                                <td class="color_squares" style="background-color: #ccd9ff;"></td>
                                <td class="color_squares" style="background-color: #afbdfe;"></td>
                                <td class="color_squares" style="background-color: #7790fe;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="blue_purple">
                            <tr>
                                <td class="color_squares" style="background-color: #e6e6ff;"></td>
                                <td class="color_squares" style="background-color: #d6d6ff;"></td>
                                <td class="color_squares" style="background-color: #adadff;"></td>
                                <td class="color_squares" style="background-color: #9966ff;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="purple">
                            <tr>
                                <td class="color_squares" style="background-color: #f3e6ff;"></td>
                                <td class="color_squares" style="background-color: #e6ccff;"></td>
                                <td class="color_squares" style="background-color: #dd99ff;"></td>
                                <td class="color_squares" style="background-color: #db4dff;"></td>
                            </tr>
                        </table>
                    </div>
                    <div class="sub_wrap px-3">
                        <table class="color_options" id="pink">
                            <tr>
                                <td class="color_squares" style="background-color: #ffe6f0;"></td>
                                <td class="color_squares" style="background-color: #ffcce0;"></td>
                                <td class="color_squares" style="background-color: #ff66a3;"></td>
                                <td class="color_squares" style="background-color: #ff1a75;"></td>
                            </tr>
                        </table>
                    </div>
                </div>
            </td>
        </tr>
    </table>
    <hr>
    <form action="/settings" method="post">
        <table id="settings_table">
            <tr>
                <th width="86px"><label class="float-end pe-1" for="new_username">Username:</label></th>
                <td><input class="form-control mx-auto w-auto" id="new_username" name="new_username" type="text" value="{{username}}"></td>
            </tr>
            <tr>
                <th><label class="float-end pe-1" for="old_password">Password:</label></th>
                <td><input class="form-control mx-auto w-auto" id="old_password" name="old_password" placeholder="Old Password" type="password"></td>
            </tr>
            <tr>
                <th></th>
                <td><input class="form-control mx-auto w-auto" id="new_password" name="new_password" placeholder="New Password" type="password" pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}" title="Minimum of 8 characters including at least one uppercase letter, one lowercase letter, one symbol, and a digit"></td>
            </tr>
            <tr>
                <th></th>
                <td><input class="form-control mx-auto w-auto" id="confirmation" name="confirmation" placeholder="Confirm Password" type="password"></td>
            </tr>
        </table>
        <button class="btn btn-primary bg pastelred mb-5" type="submit">Save</button>
    </form>
{% endblock %}
