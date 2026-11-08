#!/usr/bin/env python3
"""Builds the A8 cheatsheet from one data table:

  lessons/a8-cheatsheet.html            the web page
  lessons/downloads/ros2-cheatsheet.md  Markdown
  lessons/downloads/ros2-cheatsheet.txt plain text
  lessons/downloads/ros2-cheatsheet.pdf PDF (printed from a print-styled copy of the page by headless Chrome)

Run from anywhere:  scripts/build_cheatsheet.py   (needs google-chrome for the PDF; use --no-pdf to skip it)
Edit SECTIONS below, never the generated files. Every command listed was run (or its --help checked) on
ROS 2 Jazzy in the course image; see the lesson named in each section.
"""
import html
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "lessons" / "downloads"

# (section title, lesson id, lesson file, [(command, what it does), ...])
SECTIONS = [
    ("Terminal and environment", "A0", "a0-environment.html", [
        ("source /opt/ros/jazzy/setup.bash", "Make ROS 2 available in this terminal (already done in the course container)"),
        ("source install/setup.bash", "Make your own built workspace available (run in the workspace folder, after a build)"),
        ("echo $ROS_DOMAIN_ID", "Show the domain; programs only see each other in the same domain (default 0)"),
        ("export ROS_DOMAIN_ID=5", "Use domain 5 in this terminal (0 to 101)"),
        ("Ctrl+C", "Stop the program running in the terminal. (Ctrl+Z only suspends it: do not use it.)"),
        ("Tab", "Complete a command, a topic name or a type. Press twice to list the choices"),
    ]),
    ("Nodes", "A1", "a1-nodes-topics.html", [
        ("ros2 run <package> <executable>", "Start a program (a node) from a package"),
        ("ros2 run <package> <executable> --ros-args -r __node:=<new_name>", "Start it under another node name (run two copies)"),
        ("ros2 node list", "List the running nodes"),
        ("ros2 node info /<node>", "Show a node's topics, services, actions and parameters"),
    ]),
    ("Topics", "A1", "a1-nodes-topics.html", [
        ("ros2 topic list", "List the topics (add -t to show their types)"),
        ("ros2 topic type /<topic>", "Show a topic's message type"),
        ("ros2 topic info /<topic>", "Type, publishers and subscribers (add -v for their QoS settings)"),
        ("ros2 topic echo /<topic>", "Print the messages as they arrive"),
        ("ros2 topic echo /<topic> --once", "Print one message and stop"),
        ("ros2 topic echo /<topic> --field <field>", "Print only one field of each message"),
        ("ros2 topic hz /<topic>", "Measure how many messages arrive per second"),
        ("ros2 topic pub --once /chatter std_msgs/msg/String \"{data: hello}\"", "Publish one message. The YAML in quotes is field: value; this type has one field, data (see: ros2 interface show std_msgs/msg/String)"),
        ("ros2 topic pub -r 1 /chatter std_msgs/msg/String \"{data: hello}\"", "The same, once per second until Ctrl+C"),
        ("ros2 topic list --include-hidden-topics", "Also list hidden topics (the ones an action creates)"),
    ]),
    ("Messages, services and interfaces", "A2", "a2-messages-services.html", [
        ("ros2 interface list", "List every message, service and action type"),
        ("ros2 interface package <package>", "List the types a package defines"),
        ("ros2 interface show <package>/msg/<Type>", "Show the fields of a message (use /srv/ or /action/ for the others)"),
        ("ros2 service list", "List the services (add -t to show their types)"),
        ("ros2 service type /<service>", "Show a service's type"),
        ("ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts \"{a: 2, b: 3}\"", "Call a service. The YAML is the request: its fields (here a and b) are listed above the --- line of ros2 interface show"),
        ("ros2 service list --include-hidden-services", "Also list hidden services (the ones an action creates)"),
    ]),
    ("Actions", "A3", "a3-actions.html", [
        ("ros2 action list", "List the actions (add -t to show their types)"),
        ("ros2 action info /<action>", "Show an action's type, servers and clients"),
        ("ros2 action send_goal /<action> <type> \"{<field>: <value>}\"", "Send a goal and wait for the result. The YAML is the goal: its fields are above the first --- line of ros2 interface show <type>"),
        ("ros2 action send_goal --feedback /<action> <type> \"{<field>: <value>}\"", "Same, and print the feedback while it runs"),
    ]),
    ("Parameters", "A4", "a4-parameters-launch.html", [
        ("ros2 param list", "List the parameters of every node (or: ros2 param list /<node>)"),
        ("ros2 param get /<node> <name>", "Read a parameter"),
        ("ros2 param describe /<node> <name>", "Show its type, description and limits"),
        ("ros2 param set /<node> <name> <value>", "Change it while the node runs (lost when the node stops)"),
        ("ros2 param dump /<node>", "Print all of a node's parameters as YAML"),
        ("ros2 run <package> <executable> --ros-args -p <name>:=<value>", "Set a parameter when the node starts"),
        ("ros2 run <package> <executable> --ros-args --params-file <file.yaml>", "Set parameters from a YAML file (top-level key = node name)"),
    ]),
    ("Launch files", "A4", "a4-parameters-launch.html", [
        ("ros2 launch <package> <file.launch.py>", "Start everything a launch file describes"),
        ("ros2 launch <package> <file.launch.py> <arg>:=<value>", "Give the launch file an argument"),
        ("ros2 launch <package> <file.launch.py> --show-args", "List its arguments and their defaults, without starting anything"),
    ]),
    ("Packages and workspaces", "A5", "a5-packages-workspaces.html", [
        ("ros2 pkg list", "List the installed packages"),
        ("ros2 pkg prefix <package>", "Show where a package is installed (add --share for its share folder)"),
        ("ros2 pkg executables <package>", "List the programs a package offers to ros2 run"),
        ("ros2 pkg create --build-type ament_python --node-name <node> <package>", "New Python package with one program (ament_cmake for C++)"),
        ("colcon build", "Build every package under src/ (run in the workspace folder)"),
        ("colcon build --packages-select <package>", "Build only one package"),
        ("colcon build --symlink-install", "Link Python, launch and YAML files instead of copying (edit without rebuilding)"),
        ("colcon list", "List the packages colcon found"),
        ("rosdep install --from-paths src --ignore-src -y", "Install the system packages the workspace needs"),
        ("echo $AMENT_PREFIX_PATH | tr : '\\n'", "Show the workspaces in the search order, front first"),
    ]),
    ("Frames and TF2", "A6", "a6-frames-tf2.html", [
        ("ros2 run tf2_ros tf2_echo <from_frame> <to_frame>", "Print where <to_frame> is, as seen from <from_frame>"),
        ("ros2 run tf2_ros static_transform_publisher --x 0.1 --frame-id <parent> --child-frame-id <child>", "Publish a fixed frame (also --y --z --roll --pitch --yaw)"),
        ("ros2 run tf2_tools view_frames", "Draw the frame tree into frames_<date>.pdf"),
        ("ros2 run tf2_ros tf2_monitor", "Show, per frame, how long its transforms take to arrive"),
        ("ros2 topic echo /tf_static --once", "Look at the transform messages of fixed frames"),
        ("ros2 run rviz2 rviz2 -d <file.rviz>", "Open RViz with a saved configuration"),
    ]),
    ("ros2_control", "A7", "a7-ros2-control.html", [
        ("ros2 control list_controllers", "List the controllers and whether each is active (add -v for the interfaces each claims)"),
        ("ros2 control list_hardware_components", "List the hardware components (mock or real) and their interfaces"),
        ("ros2 control list_hardware_interfaces", "List every command and state interface, and which are claimed"),
        ("ros2 control switch_controllers --deactivate <controller> --activate <controller>", "Hand the joints from one controller to another"),
        ("ros2 topic echo /joint_states --once", "Read the joint names, angles, velocities and efforts"),
    ]),
    ("The Kinova arm", "A6, A7", "a7-ros2-control.html", [
        ("ros2 launch kortex_description view_robot.launch.py gripper:=robotiq_2f_85", "The arm in RViz with joint sliders (no controllers)"),
        ("ros2 launch kortex_bringup gen3.launch.py robot_ip:=yyy.yyy.yyy.yyy use_fake_hardware:=true gripper:=robotiq_2f_85", "The arm with controllers and fake hardware: the same launch file as the real arm"),
        ("ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \"{joint_names: [joint_1, joint_2, joint_3, joint_4, joint_5, joint_6, joint_7], points: [{positions: [0, 0, 0, 0, 0, 0, 0], time_from_start: {sec: 2}}]}\"", "Move all seven joints to zero in 2 seconds"),
    ]),
]

KEYS = {"Ctrl+C", "Tab"}  # keystrokes, not commands: no Copy button
TITLE = "ROS 2 basics cheatsheet"
INTRO = ("Commands from lessons A0 to A7 (ROS 2 Jazzy). Words in <angle brackets> are placeholders: "
         "replace them, without the brackets. Text in quotes like \"{data: hello}\" is YAML: field names and their values, "
         "as the message, request or goal defines them (ros2 interface show <type> lists the fields). Course: https://github.com/Turgibot/ros2-tutorial")


def to_md():
    out = [f"# {TITLE}", "", INTRO, ""]
    for title, lid, _f, rows in SECTIONS:
        out += [f"## {title} ({lid})", "", "| Command | What it does |", "|---|---|"]
        for cmd, what in rows:
            out.append("| `" + cmd.replace("|", "\\|") + "` | " + what.replace("|", "\\|") + " |")
        out.append("")
    return "\n".join(out)


def to_txt():
    out = [TITLE.upper(), "=" * len(TITLE), "", INTRO, ""]
    for title, lid, _f, rows in SECTIONS:
        head = f"{title} ({lid})"
        out += [head, "-" * len(head)]
        for cmd, what in rows:
            out += [f"  {cmd}", f"      {what}"]
        out.append("")
    return "\n".join(out)


def to_html(for_pdf=False):
    h = []
    for title, lid, f, rows in SECTIONS:
        sid = title.lower().replace(" ", "-").replace(",", "")
        h.append(f'<section class="cs" id="{sid}"><h2>{html.escape(title)} <a class="lid" href="{f}">{html.escape(lid)}</a></h2>')
        h.append('<table class="cs-t">')
        for cmd, what in rows:
            c = html.escape(cmd, quote=False)
            first = f'<kbd>{c}</kbd>' if cmd in KEYS else f'<pre class="cmd"><code>{c}</code></pre>'
            h.append(f'<tr><td>{first}</td><td>{html.escape(what, quote=False)}</td></tr>')
        h.append("</table></section>")
    body = "\n".join(h)
    intro = html.escape(INTRO.split(" Course:")[0], quote=False).replace("&lt;angle brackets&gt;", "&lt;angle brackets&gt;")
    return body, intro


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A8 · ROS 2 cheatsheet</title>
<link rel="stylesheet" href="assets/style.css">
<style>
.dl {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 1rem 0 1.4rem; }}
.dl a {{ display: inline-block; padding: 7px 16px; border: 1px solid var(--accent); border-radius: 8px;
  color: var(--accent); text-decoration: none; font-weight: 600; background: var(--accent-soft); }}
.dl a:hover {{ background: var(--accent); color: var(--bg); }}
.dl small {{ font-weight: 400; opacity: .8; }}
.cs h2 {{ display: flex; align-items: baseline; gap: 10px; }}
.cs .lid {{ font-size: .75rem; font-weight: 600; padding: 1px 8px; border-radius: 10px; background: var(--accent-soft);
  color: var(--accent); text-decoration: none; }}
table.cs-t {{ width: 100%; border-collapse: collapse; }}
table.cs-t td {{ vertical-align: top; padding: 6px 8px 6px 0; border-top: 1px solid var(--line); }}
table.cs-t td:first-child {{ width: 58%; }}
table.cs-t pre.cmd {{ margin: 0; }}
@media (max-width: 700px) {{ table.cs-t, table.cs-t tbody, table.cs-t tr, table.cs-t td {{ display: block; width: 100% !important; }}
  table.cs-t td {{ border: 0; padding: 0; }} table.cs-t tr {{ border-top: 1px solid var(--line); padding: 8px 0; }} }}
</style>
</head>
<body>
<header class="site"><a href="index.html">ROS 2 + Kinova Gen3</a><small>by <a href="https://turgibot.com">Guy Tordjman aka Turgibot</a></small><span>Part A · ROS 2 basics</span></header>
<main>

<h1>A8 · ROS 2 cheatsheet</h1>
<p class="lead">All the commands of Part A on one page, grouped as in the lessons. Keep it open next to your terminal.</p>
<div class="dl">
<a href="downloads/ros2-cheatsheet.pdf" download>PDF <small>(print or read)</small></a>
<a href="downloads/ros2-cheatsheet.md" download>Markdown <small>(.md)</small></a>
<a href="downloads/ros2-cheatsheet.txt" download>Plain text <small>(.txt)</small></a>
</div>
<p>{intro} Click <strong>Copy</strong> on a command to copy it. The tag next to each heading is the lesson that teaches it. Everything here works the same in the Docker container and in a local install.</p>

{body}

<nav class="pager">
<a href="a7-ros2-control.html"><small>Previous</small>A7 · ros2_control</a>
<a class="next" href="b0-kortex-workspace.html"><small>Next</small>B0 · The Kinova workspace</a>
</nav>
</main>
<footer class="site"><p>Created by <a href="https://turgibot.com">Guy Tordjman aka Turgibot</a>. Text CC BY 4.0, code MIT. Source and issues: <a href="https://github.com/Turgibot/ros2-tutorial">github.com/Turgibot/ros2-tutorial</a></p></footer>
<script src="assets/lesson.js"></script>
</body>
</html>
"""

PRINT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ font: 8.6pt/1.35 "DejaVu Sans", system-ui, sans-serif; color: #1d2127; margin: 0; }}
h1 {{ font-size: 15pt; margin: 0 0 2pt; }}
p.intro {{ margin: 0 0 6pt; color: #444; font-size: 8pt; }}
.cols {{ column-count: 2; column-gap: 9mm; }}
section {{ break-inside: avoid; margin: 0 0 7pt; }}
h2 {{ font-size: 9.6pt; margin: 0 0 2pt; padding: 2pt 5pt; background: #e6eefb; color: #1f4f9f; border-radius: 3pt; }}
h2 .lid {{ float: right; font-weight: 600; font-size: 7.5pt; }}
table {{ width: 100%; border-collapse: collapse; }}
td {{ vertical-align: top; padding: 2pt 0; border-top: 0.4pt solid #d5d9df; }}
pre {{ margin: 0 0 1pt; font: 7.4pt/1.3 "DejaVu Sans Mono", monospace; white-space: pre-wrap; word-break: break-all; color: #0b3a7a; }}
.what {{ color: #333; }}
.foot {{ margin-top: 4pt; font-size: 7pt; color: #666; }}
</style></head><body>
<h1>{title}</h1>
<p class="intro">{intro}</p>
<div class="cols">
{body}
</div>
<p class="foot">Course: github.com/Turgibot/ros2-tutorial</p>
</body></html>
"""


def print_body():
    h = []
    for title, lid, _f, rows in SECTIONS:
        h.append(f'<section><h2>{html.escape(title)} <span class="lid">{html.escape(lid)}</span></h2><table>')
        for cmd, what in rows:
            h.append(f'<tr><td><pre>{html.escape(cmd, quote=False)}</pre><div class="what">{html.escape(what, quote=False)}</div></td></tr>')
        h.append("</table></section>")
    return "\n".join(h)


def main():
    OUT.mkdir(exist_ok=True)
    body, intro = to_html()
    (ROOT / "lessons" / "a8-cheatsheet.html").write_text(PAGE.format(body=body, intro=intro))
    (OUT / "ros2-cheatsheet.md").write_text(to_md() + "\n")
    (OUT / "ros2-cheatsheet.txt").write_text(to_txt() + "\n")
    print("wrote html, md, txt")
    if "--no-pdf" in sys.argv:
        return
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "print.html"
        src.write_text(PRINT.format(title=TITLE, intro=html.escape(INTRO), body=print_body()))
        subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={OUT / 'ros2-cheatsheet.pdf'}", f"file://{src}"],
                       check=True, capture_output=True)
    print("wrote pdf")


if __name__ == "__main__":
    main()
