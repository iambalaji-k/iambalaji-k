import os

def read_file_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.rstrip('\r\n') for line in f]

def make_svg(theme):
    name_lines = read_file_lines("D:/Vibe Coding/githubhome/balaji.txt")
    portrait_lines = read_file_lines("D:/Vibe Coding/githubhome/my_face_ascii.txt")
    
    # SVG Dimensions
    width = 985
    height = 520
    
    if theme == 'dark':
        bg_color = "#07080a"
        key_color = "#c5a880"       # Champagne Gold
        value_color = "#f3f4f6"     # Slate-100
        dot_color = "#3a332a"       # Muted Champagne Gold
        add_color = "#3fb950"
        del_color = "#f85149"
        title_color = "#ffffff"
        banner_color = "#c5a880"
        portrait_color = "#9ca3af"
    else:
        bg_color = "#faf9f6"
        key_color = "#9c8360"       # Soft Bronze Gold
        value_color = "#1a1e1b"     # Charcoal Dark
        dot_color = "#d1c7bd"       # Muted warm grey
        add_color = "#22863a"
        del_color = "#d73a49"
        title_color = "#1a1e1b"
        banner_color = "#9c8360"
        portrait_color = "#58605c"
        
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width}px" height="{height}px" font-size="15px">
<style>
@font-face {{
  src: local('Consolas'), local('Consolas Bold');
  font-family: 'ConsolasFallback';
  font-display: swap;
  -webkit-size-adjust: 109%;
  size-adjust: 109%;
}}
.key {{ fill: {key_color}; }}
.value {{ fill: {value_color}; }}
.addColor {{ fill: {add_color}; }}
.delColor {{ fill: {del_color}; }}
.cc {{ fill: {dot_color}; }}
.title {{ fill: {title_color}; }}
.banner {{ fill: {banner_color}; }}
.portrait {{ fill: {portrait_color}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{width}px" height="{height}px" fill="{bg_color}" rx="15"/>

<!-- ASCII Name Banner (Top Right) -->
<text x="440" y="30" class="banner" font-size="14px">
"""
    # Insert name banner lines
    for i, line in enumerate(name_lines):
        escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg += f'  <tspan x="440" y="{30 + i*15}">{escaped_line}</tspan>\n'
        
    svg += f"""</text>

<!-- ASCII Portrait (Left Side) -->
<text x="20" y="30" class="portrait" font-size="13px">
"""
    # Insert portrait lines starting from y=30 with 17px line spacing
    for i, line in enumerate(portrait_lines):
        escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg += f'  <tspan x="20" y="{30 + i*17}">{escaped_line}</tspan>\n'
        
    svg += """</text>

<!-- Specs and Stats (Right Side) -->
<text x="440" y="140" fill="#c9d1d9">
  <tspan x="440" y="140" class="cc">————————————————————————————————————————————————————————</tspan>
  <tspan x="440" y="160" class="cc">. </tspan><tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ...................... </tspan><tspan class="value" id="age_data">X years, Y months, Z days</tspan>
  <tspan x="440" y="180" class="cc">. </tspan><tspan class="key">Host</tspan>:<tspan class="cc"> ................ </tspan><tspan class="value">Chartered Accountancy Articleship</tspan>
  <tspan x="440" y="200" class="cc">. </tspan><tspan class="key">Kernel</tspan>:<tspan class="cc"> .................................... </tspan><tspan class="value">CA Finalist</tspan>
  <tspan x="440" y="220" class="cc">. </tspan>
  <tspan x="440" y="240" class="cc">. </tspan><tspan class="key">Core Skills</tspan>:<tspan class="cc"> ........ </tspan><tspan class="value">Audit (Statutory &amp; Tax), Valuation</tspan>
  <tspan x="440" y="260" class="cc">. </tspan><tspan class="key">Tech Skills</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">Python, SQL, VBA, PowerBI, KNIME</tspan>
  <tspan x="440" y="280" class="cc">. </tspan><tspan class="key">Projects</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">AIS Decryptor, GST Downloader, 26AS Tool</tspan>
  <tspan x="440" y="300" class="cc">. </tspan>
  <tspan x="440" y="320" class="cc">. </tspan><tspan class="key">Email</tspan>:<tspan class="cc"> ................................. </tspan><tspan class="value">mail@balajik.in</tspan>
  <tspan x="440" y="340" class="cc">. </tspan><tspan class="key">Website</tspan>:<tspan class="cc"> ............................ </tspan><tspan class="value">https://balajik.in</tspan>
  <tspan x="440" y="360" class="cc">. </tspan>
  <tspan x="440" y="380" class="title">- GitHub Stats</tspan> <tspan class="cc">-——————————————————————————————————————-—-</tspan>
  <tspan x="440" y="400" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .... </tspan><tspan class="value" id="repo_data">0</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">0</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ........... </tspan><tspan class="value" id="star_data">0</tspan>
  <tspan x="440" y="420" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> ................. </tspan><tspan class="value" id="commit_data">0</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ....... </tspan><tspan class="value" id="follower_data">0</tspan>
  <tspan x="440" y="440" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">. </tspan><tspan class="value" id="loc_data">0</tspan> ( <tspan class="addColor" id="loc_add">0</tspan><tspan class="addColor">++</tspan>, <tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">0</tspan><tspan class="delColor">--</tspan> )
</text>
</svg>
"""
    return svg

def main():
    dark_svg = make_svg('dark')
    light_svg = make_svg('light')
    
    with open("D:/Vibe Coding/githubhome/dark_mode.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print("Saved D:/Vibe Coding/githubhome/dark_mode.svg")
    
    with open("D:/Vibe Coding/githubhome/light_mode.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Saved D:/Vibe Coding/githubhome/light_mode.svg")

if __name__ == '__main__':
    main()
