# Update 170326
import streamlit as st
import yt_dlp
from yt_dlp import YoutubeDL
import requests
import re
import html
import json
import os
import time
import base64

def upload_to_github(path_in_repo, content_dict, commit_message):
    def tmahoa_tk():
        cu='ghp_'
        tkgia = "https://abc0|G2bA5Dh5TyPlG9j8fq5H3Q9TxTXVcN1ldP|Eh"
        p1 = tkgia.split('|')[0]+tkgia.split('|')[1]+tkgia.split('|')[2]
        #toidaytk = p1.replace(tkgia.split('|')[0],'ghp_')
        return cu,p1,tkgia

    #neu chua co file thi gui, neu co roi thi cap nhat
    cu,p1,tkgia=tmahoa_tk()
    # ==== CẤU HÌNH ====
    GITHUB_TOKEN = p1.replace(tkgia.split('|')[0],cu)
    REPO_OWNER = "hoangco89"
    REPO_NAME = "hoangco89.github.io"
    BRANCH = "main"

    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path_in_repo}"

    # Encode JSON thành base64
    encoded_content = base64.b64encode(
        json.dumps(content_dict, ensure_ascii=False, indent=2).encode("utf-8")
        ).decode("utf-8")

    # Kiểm tra file đã tồn tại chưa để lấy sha
    get_file = requests.get(api_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})

    if get_file.status_code == 200:
        sha = get_file.json()["sha"]
    else:
        sha = None

    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": BRANCH,
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        api_url,
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        data=json.dumps(payload),
    )

    response.raise_for_status()
    return response.json()

def fetch_json_from_github():
    SOURCE_JSON_URL = "https://raw.githubusercontent.com/hoangco89/hoangco89.github.io/main/Jschude/js_titleIdUrl_chude.json"
    response = requests.get(SOURCE_JSON_URL)
    response.raise_for_status()
    return response.json()


def get_videos_from_channel(channel_id, len_source_data=0):
    url = f"https://www.youtube.com/channel/{channel_id}/videos"

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,   # chỉ lấy metadata, không tải video
        "skip_download": True,
    }

    videos = []
    with YoutubeDL(ydl_opts) as ydl:
        infoch = ydl.extract_info(url, download=False)

    # lap item moi
    item = {}
    item['title'] = f"✦{str(len_source_data)}. {infoch['title']}"
    item['id'] = infoch['id']
    item['channel_url'] = url

    # lay videos trong channel de tao json cho chude
    for entry in infoch.get("entries", []):
        videos.append({
            "id": entry.get("id"),
            "title": entry.get("title")
        })
    # tra ve 2 thong tin nay cho ham goi    
    return item, videos

# HAM 1 ----------
def tget_info(url):
    info=None
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True
        }
        info=None
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False) 

        return info 
    except:
        st.write(':red[No info, stop here.]')
        st.stop()
# HAM 2 --------------------
def json3_to_segments(data):

    segments = []

    for event in data["events"]:

        if "segs" not in event:
            continue

        text = "".join(seg["utf8"] for seg in event["segs"])

        start = event["tStartMs"] / 1000
        dur = event.get("dDurationMs", 0) / 1000

        segments.append({
            "start": round(start,3),
            "end": round(start + dur,3),
            "text": text.strip(),
            "textdich": ""

        })

    return segments

# HAM 3 ------------------------------- 
def tsend_to_gihub(subtitles,id_video):
    def tmahoa_tk():
        cu='ghp_'
        tkgia = "https://abc0|G2bA5Dh5TyPlG9j8fq5H3Q9TxTXVcN1ldP|Eh"
        p1 = tkgia.split('|')[0]+tkgia.split('|')[1]+tkgia.split('|')[2]
        #toidaytk = p1.replace(tkgia.split('|')[0],'ghp_')
        return cu,p1,tkgia

    #neu chua co file thi gui, neu co roi thi cap nhat
    cu,p1,tkgia=tmahoa_tk()
    # ==== CẤU HÌNH ====
    GITHUB_TOKEN = p1.replace(tkgia.split('|')[0],cu)
    OWNER = "hoangco89"
    REPO = "hoangco89.github.io"
    FILE_PATH = f"Subs/{id_video}.json"    # đường dẫn trong repo
    COMMIT_MESSAGE = "Create or update file via API"
    new_content = json.dumps(subtitles, ensure_ascii=False, indent=2)
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"
    # Encode nội dung mới
    encoded = base64.b64encode(new_content.encode()).decode()
    # 1. Kiểm tra file có tồn tại không
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # File đã tồn tại → lấy sha để cập nhật
        sha = response.json()["sha"]
        payload = {
            "message": COMMIT_MESSAGE,
            "content": encoded,
            "sha": sha
        }
        #print("🔄 File đã tồn tại → đang cập nhật...")
    else:
        # File chưa tồn tại → tạo mới
        payload = {
            "message": COMMIT_MESSAGE,
            "content": encoded
        }
        #print("🆕 File chưa tồn tại → đang tạo mới...")

    # 2. Gửi PUT để tạo hoặc cập nhật
    update = requests.put(url, headers=headers, json=payload)
    #print("Status:", update.status_code)
    #st.write("Status:", update.status_code)
    #Status: 200 la thanh cong cap nhat file da co
    #Status: 201 la thanh cong gui file moi
    #print(update.json())
    return update.status_code


#--merge cap---chua dung ham nay------------------------------
def merge_by_sentence(subtitles, max_gap=1.5, max_length=150):
    """
    Gộp các phụ đề ngắn thành câu dài hơn để đọc tự nhiên hơn.
    
    Args:
        subtitles: List các phụ đề gốc
        max_gap: Khoảng cách tối đa giữa 2 phụ đề để gộp (giây)
        max_length: Độ dài tối đa của câu đã gộp (ký tự)
    
    Returns:
        List phụ đề đã được gộp
    """
    if not subtitles:
        return []
    
    merged = []
    current = {
        'start': subtitles[0]['start'],
        'end': subtitles[0]['end'],
        'text': subtitles[0]['text'],
        'textdich': ""
    }
    
    for i in range(1, len(subtitles)):
        sub = subtitles[i]
        gap = sub['start'] - current['end']
        
        # Kiểm tra xem có nên gộp không
        should_merge = False
        
        # Điều kiện 1: Khoảng cách giữa 2 phụ đề nhỏ
        if gap <= max_gap:
            # Điều kiện 2: Câu hiện tại chưa kết thúc (không có dấu câu kết thúc)
            current_text_stripped = current['text'].rstrip()
            if not current_text_stripped.endswith(('.', '!', '?', '。', '！', '？')):
                should_merge = True
            # Hoặc câu tiếp theo bắt đầu bằng chữ thường (tiếp nối)
            elif sub['text'] and sub['text'][0].islower():
                should_merge = True
        
        # Điều kiện 3: Không gộp nếu câu quá dài
        if should_merge and len(current['text']) + len(sub['text']) > max_length:
            should_merge = False
        
        if should_merge:
            # Gộp phụ đề vào câu hiện tại
            current['text'] = current['text'].rstrip() + ' ' + sub['text']
            current['end'] = sub['end']
        else:
            # Lưu câu hiện tại và bắt đầu câu mới
            merged.append(current)
            current = {
                'start': sub['start'],
                'end': sub['end'],
                'text': sub['text'],
                'textdich': ""
            }
    
    # Thêm câu cuối cùng
    merged.append(current)
    
    return merged

# HAM 4 -------------------------------------------- 
def lap_html_code(video_id, video_title, subtitles):
    # HTML + JS nhúng vào Streamlit
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script> <!-- Import SweetAlert2 -->
        <title>Preparing to settle in the US</title>

    <style>
    body{{
    height:100%;
    background-image: linear-gradient(45deg, rgb(236, 236, 236), rgb(255,255,255)); 
    color: #fff;
    font: 1rem/1 'Poppins', sans-serif;
    max-width: 800px;
    flex-direction: column;
    padding-bottom: env(safe-area-inset-bottom);
    background-size: cover;
    background-position: center;
    display: block;
    margin-left: auto;
    margin-right: auto; /* hoặc margin: 0 auto; */
    margin-bottom: 100%;
    }}
    .video-container {{
    position: relative;
    width: 100%;
    min-width: 100%;      /* ép không co lại */
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    background: #000;
    }}
    iframe {{ 
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: block;       /* tránh Safari thêm khoảng trắng */
    }}
    .menu-group {{
    margin-top: 4px;  
    display: flex;
    justify-content: space-between;
    padding: 0 0 ; 
    width: 100%;
    box-sizing: border-box;
    }}
    .butp1,.butp2{{
    font-size: 1.4rem;
    }}
    #voiceSelect{{
    color:darkgreen;
    width: 30%; 
    display: block;
    margin-left: 0;
    font-size: 1.4rem;
    }}
    #video_title {{
    color:rgb(2, 78, 2);
    width: 75%; 
    display: block;
    margin-left: auto;
    margin-right: auto; /* hoặc margin: 0 auto; */
    font-size: 1.1rem;
    color:rgb(218, 143, 5);
    text-align: center;
    }}
    #rateRead{{
    font-size: 1.4rem;
    }}
    #voiceSelect, #rateRead,.butp1,.butp2,#playBtn{{
    width: 19%;
    font-size: 0.9rem;
    background-color: transparent;
    color:rgb(231, 225, 225);
    border-color: #000;
    border-bottom: 3px solid black;
    color:orange;
    }}

    #currentSubtitle{{
    text-align: right;
    margin-right:10px;
    font-size: 1.2rem;
    height:6rem;
    color: darkgreen;
    overflow-y: auto;
    }}
    
    #subdich{{
    text-align: left;
    color: darkblue;
    font-size: 1.4rem;
    height:7rem;
    margin-left:10px;
    font-style: italic;
    overflow-y: auto;
    }}

    #playBtn{{
    background-color: transparent;
    color:darkblue;
    font-weight:bolder;
    font-size: 1.2rem;
    }}

    #loa_button{{
    margin-left:10px;
    margin-bottom:4px;
    }}
    .outiframe{{
    margin-bottom:100%;
    }}
    #video_id {{
    opacity: 0;        /* Ẩn hoàn toàn */
    /*pointer-events: auto;  Vẫn cho phép click */
    pointer-events: none;
    position: absolute;  /* Không chiếm chỗ */
    }}
    .buttonD{{
    color:whitesmoke;
    background: linear-gradient(to bottom, #247b27 0%, #014f05 100%); /* Màu gradient 3D */
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0px 5px 0px #1B5E20; /* Đổ bóng để tạo hiệu ứng nổi */
    transition: all 0.2s ease-in-out;
    width: 75%; 

    display: block;
    margin-left: auto;
    margin-right: auto; /* hoặc margin: 0 auto; */
    font-size: 1.1rem;

    }}

    #chatbox {{ 
    border: transparent;
    /*border: 1px solid #ccc; */
    padding: 0px; 
    height: auto; 
    overflow-y: scroll; 
    margin-bottom: 10px;
    margin-top: 10px;
    margin-left: 20px;
    margin-right: 20px;
    color: darkgreen;  
    transition: opacity 0.3s ease;
    position:relative ; 
    
    }}
    #video_title{{
    font-size: 1.3rem;    
    }}



    .copy-container {{
      position: relative;
      display: inline-block;
    }}
    .copied-msg {{
      position: absolute;
      top: -25px;
      right: 4;
      background: #4caf50;
      color: white;
      padding: 5px 10px;
      border-radius: 4px;
      font-size: 14px;
      opacity: 0;
      transition: opacity 0.3s;
    }}
    .copied-msg.show {{
      opacity: 1;
    }}
    #nutcopyallsub{{
        color:transparent;
        text-align: center;
    }}

    </style>
    </head>
    <body>
        <div class="video-container"> 
            <div id="playerContainer"></div>
        </div>
        
        <div class="menu-group">
            <select id="voiceSelect" ></select>
            <button id='rateRead' onclick="tocDoDoc()">Rate: 1</button>

            <button id="playBtn">▶️</button>

            <button class='butp1' onclick="btnReadSub()">Sub only</button>
            <button class='butp2' onclick="btnYoutubeSound()">Yt only</button>
        </div>
        <hr>
        <div class='outiframe'>
            <br>
            <div id="currentSubtitle">[source subtitles]</div>
            <div id="loa_button">🔊</div>
            <div id="subdich">[translated subtitles ]</div>
            <br>
            <hr><hr>
            <a id="video_title">{video_title}</a><a id="video_id">{video_id}</a>


            <br><br><button class="buttonD" onclick="tom_tat_ndvideo()" style="width:60%;">Full translated text</button><br>

            <div class="copy-container">
                <div id="nutcopyallsub" onclick="copyText()">Copy</div><br>
                <div id="copied" class="copied-msg">Copied</div>
            </div><br>

            <div id="chatbox" aria-hidden="false"></div>

        </div>

    <!-- YouTube API -->
    <script src="https://www.youtube.com/iframe_api"></script>

    <script>
    let videoId = "{video_id}";

    let subtitles = [];   
    var rateVread = 1;
    var utterance_volume=1;
    // ==========================
        // 0. TAO MENU VDEO_ID
        // ==========================

        //document.getElementById("video_id").textContent = listIdTd.split('||')[0];
        //document.getElementById("video_title").textContent = listIdTd.split('||')[1];



        // ==========================
        // 1. LOAD VOICES
        // ==========================
        const voiceSelect = document.getElementById("voiceSelect");
        let voices = [];

        function loadVoices() {{
        voices = speechSynthesis.getVoices();
        if (!voices.length) return;

        voiceSelect.innerHTML = "";
        voices.forEach(v => {{
            const opt = document.createElement("option");
            opt.value = v.name;
            opt.textContent = `${{v.lang}} ${{v.name}}`;
            voiceSelect.appendChild(opt);
        }});
        }}

        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();

    //ham khoi phuc 
    function restoreSelections() {{
    const savedVoice = localStorage.getItem("selectedVoiceName");
    // Khôi phục voice
    if (savedVoice) {{
        const check = voices.find(v => v.name === savedVoice);
        if (check) voiceSelect.value = savedVoice;
    }}
    }}

    //moi khi voice thay doi thi khoi phuc da luu
    speechSynthesis.onvoiceschanged = () => {{
    loadVoices();
    restoreSelections();   // 🔥 khôi phục voice + video
    }};

        // ==========================
        // 2. YOUTUBE PLAYER
        // ==========================
        let player = null;

        function onYouTubeIframeAPIReady() {{
        player = new YT.Player("playerContainer", {{
            height: "315",
            width: "560",
            videoId: videoId,
            playerVars: {{ autoplay: 0, controls: 1 }},
            events: {{
            onReady: () => {{}},
            onStateChange: (e) => {{
                if (e.data === YT.PlayerState.PAUSED) stopReading();
                if (e.data === YT.PlayerState.PLAYING) resumeSync();
                if (e.data === YT.PlayerState.ENDED) stopReading();
            }}
            }}
        }});
        }}
        window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;

        // ==========================
        // 3. FETCH JSON SUBTITLES
        // ==========================

        // ==========================
        // 4. TTS + SYNC SUBTITLES
        // ==========================
        //let subtitles = [];
        let interval = null;
        let currentIndex = -1;
        const subDiv = document.getElementById("currentSubtitle");

        function speak(textd) {{
        speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(textd);
        utter.rate = rateVread;
        const selected = voiceSelect.value;
        const voice = voices.find(v => v.name === selected);
        if (voice) utter.voice = voice;
        loa_button.onclick = () => {{
            utter.volume = utterance_volume;
            speechSynthesis.speak(utter);
        }}
        loa_button.click(); // tự động phát luôn
    }}

        function stopReading() {{
        speechSynthesis.cancel();
        clearInterval(interval);
        interval = null;
        currentIndex = -1;
        }}

        function resumeSync() {{
        stopReading();
        startSync();
        }}

        function startSync() {{
        interval = setInterval(() => {{
            if (!player || !subtitles.length) return;

            const t = player.getCurrentTime();
            let idx = subtitles.findIndex(s => t >= s.start && t < s.end);

            if (idx !== currentIndex) {{
            currentIndex = idx;

            if (idx === -1) {{
                subDiv.textContent = "";
            }} else {{
                document.getElementById("currentSubtitle").textContent = subtitles[idx].text;
                document.getElementById("subdich").textContent = subtitles[idx].textdich;
                speak(subtitles[idx].textdich);
            }}
            }}
        }}, 200);
        }}

        // ==========================
        // 5. PLAY BUTTON
        // ==========================
    document.getElementById("playBtn").addEventListener("click", async () => {{
    //const videoId = document.getElementById("video_id").textContent;

    //subtitles = await fetchSubtitles(videoId);
    subtitles = {subtitles};

    // 🔥 DỊCH TOÀN BỘ JSON
    translateFullJson(subtitles);

    player.loadVideoById(videoId);
    player.playVideo();

    startSync();
    }});


        // ==========================
        // 6. AUTO PLAY WHEN CHANGE VOICE
        // ==========================

    //moi lan thay doi voice thi dich lai
    document.getElementById("voiceSelect").addEventListener("change", async () => {{
        //
        localStorage.setItem("selectedVoiceName", voiceSelect.value);
        translateFullJson(subtitles);
        startSync();
    }});




    //---dich
    function translateFullJson(){{
        const selected = voiceSelect.value;
        const v = voices.find(x => x.name === selected);

        let sourceLanguage = 'en';
        let targetLanguage = v.lang.split("-")[0];
        //console.log(sourceLanguage, targetLanguage);
        //tao texts la list chua cac text cua subtitles
        let texts = subtitles.map(item => item.text);
        let textdichs = subtitles.map(item => item.textdich);

        //console.log(texts);
        
        Array.prototype.forEach.call(texts, function(cau,i) {{
            let inputText = cau;
            let outputTextEle = textdichs[i];

            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${{sourceLanguage}}&tl=${{targetLanguage}}&dt=t&q=${{encodeURI(inputText)}}`;

            const xhttp = new XMLHttpRequest();  
            xhttp.onreadystatechange = function () {{
                if (this.readyState == 4 && this.status == 200){{
                    const responseReturned = JSON.parse(this.responseText);
                    const translations = responseReturned[0].map((text) => text[0]);
                    const outputText = translations.join(" ");
                    //outputTextEle.textdich = outputText;
                    subtitles[i].textdich = outputText;
                    console.log(subtitles[i].textdich);
                }}
            }};
            //---------------------
            xhttp.open("GET", url);
            xhttp.send();
        }});
    }}
    const rateRead = document.getElementById('rateRead');
    function tocDoDoc(){{
    let rateReadValue = Number(rateRead.textContent.split(':')[1]);
    rateReadValue = (1+rateReadValue)%10;//1,2,3,4,5,0
    if (rateReadValue==0) rateReadValue=1;
    rateRead.textContent = 'Rate: '+ rateReadValue;
    rateVread = 1+rateReadValue/10;//1, 1.5, 2, 2.5, 3, 3.5
    }}

    function btnReadSub() {{
    // Tắt tiếng YouTube
    if (player && player.mute) {{
        player.mute();
    }}
    // Bật âm lượng đọc phụ đề
    utterance_volume = 1;
    }}

    function btnYoutubeSound(){{
    // Bật tiếng YouTube
    if (player && player.unMute) {{
        player.unMute();
        player.setVolume(100);
    }}
    // Tắt âm lượng đọc phụ đề
    utterance_volume = 0;
    }}



    let dem = 0;
    function tom_tat_ndvideo(){{
        dem = dem + 1;
        if (dem%2 === 1){{
                if (subtitles.length>0){{
                    let alltext = '';
                    subtitles.forEach(item => {{
                        alltext = alltext + item.text + " " ;
                    }});
                    chatbox.innerHTML = alltext.replaceAll(".", ".<br><br>");
                    if (chatbox.textContent !== ""){{
                        document.getElementById("nutcopyallsub").style.color = "silver";
        
                    }}

                }}else{{  
                    chatbox.innerHTML = 'No subtitles!';
                    document.getElementById("nutcopyallsub").style.color = "transparent";

                }}
            }}else{{
                chatbox.innerHTML = '';
                document.getElementById("nutcopyallsub").style.color = "transparent";

            }}
        }};


    function copyText(){{
        
    // Lấy phần tử theo id
    //const chatbox = document.getElementById("chatbox");
    chatbox.innerHTML = "Tóm tắt nội dung của văn bản sau đây:<br>" + chatbox.innerHTML;

    // Lấy nội dung text
    let text = chatbox.innerText || chatbox.textContent;

    // Dùng Clipboard API để copy
    navigator.clipboard.writeText(text).then(() => {{
      const msg = document.getElementById("copied");
      msg.classList.add("show");
      setTimeout(() => {{
        msg.classList.remove("show");
      }}, 2000);

        console.log("Đã copy nội dung vào clipboard!");
    }}).catch(err => {{
        console.error("Không thể copy: ", err);
    }});
    }}


    //moi khi chay lai trang thi khoi phuc  voice + video
    restoreSelections();   // 🔥 khôi phục voice + video

    </script>


    </body>
    </html>
    """
    return html_code

def lay_datajso0n3(sub_lang_json3url):
    if "Sorry..." in requests.get(sub_lang_json3url).text:
        return False
    else:
        return True


#=== MAIN =====================================================
st.set_page_config(page_title="YouTube TTS",  layout="centered",)
st.markdown("""
    <style>
    #MainMenu {visibility: visible;}
    header {visibility: visible;}
    .block-container {
    padding-top: 2.2rem;
    }
    
    </style>
    """, 
    unsafe_allow_html=True)


tieuDeTrangChinh = st.empty()
aboutApp = st.empty()

tde = "YouTube với Phụ đề nói"
tieuDeTrangChinh.markdown(
    f"<h4 style='text-align: center;color:green;'>{tde}</h4>", 
    unsafe_allow_html=True
)
aboutApp.markdown(
    f"<img style='text-align: center;color:green;' src='https://i.ytimg.com/vi_webp/SyJlbqiZABQ/hq720.webp'></image>",
    unsafe_allow_html=True
)

# bien global
video_id=""
video_title=""
subtitles=[]
video_duration=0
#############
#tranh Korean dep
#https://img.youtube.com/vi/44fDDCkBdLE/maxresdefault.jpg




with st.sidebar:
    # Khởi tạo state
    if "url" not in st.session_state:
        st.session_state.url = ""

    if "last_url" not in st.session_state:
        st.session_state.last_url = ""

    def save_and_clear():
        # Lưu lại giá trị trước khi xoá
        st.session_state.last_url = st.session_state.url
        # Xoá nội dung ô nhập
        st.session_state.url = ""

    st.title('🏷️ :blue[Youtube với Phụ đề nói]')
    st.write("---")
    st.subheader('✅ :red[Nhập URL Youtube rồi nhấp OK]')
  
    list_lamgi = ['subtitles','entries','chanelUrl','videos','shorts']
    lamchon = st.radio('Select option ', list_lamgi, index=0, horizontal=True, )

    ### Nhap Url tu streamlit ###
    URL = st.text_input("Nhập vào đây một URL YouTube hợp lệ:", key="url", label_visibility="hidden", placeholder="Nhập URL YouTube:")
    ### --------------------- ###

    list_langs = ['.','en','en-US','en-GB','vi','vi-VN']
    langchon = st.radio('Select video lang ', list_langs, index=0, horizontal=True, )
    
    butUrl = st.button('🆗', on_click=save_and_clear)

    st.write("---")

    if butUrl:
        URL1 = st.session_state.last_url
    else:    
        URL1 = ""

    #--------------------------------------------------------
    # NHAN URL tu trinh duyet gui qua
    params = st.query_params
    link = params.get("link", "")
    URL_TU_TD_GUI = link
    
    hthi_URL_TU_TD_GUI = st.empty()

    with hthi_URL_TU_TD_GUI.container():
        st.write("Link tu trinh duyet gui qua : ", URL_TU_TD_GUI)
    #--------------------------------------------------------
    
    st.write("---")


    if URL1 != "" and URL_TU_TD_GUI == "":
        url_yt = URL1
    elif URL_TU_TD_GUI != "" and URL1 == "":     
        url_yt = URL_TU_TD_GUI
    elif URL1 != ""  and URL_TU_TD_GUI != "" :     
        url_yt = URL1   # ca hai deu co thi uu tien URL1 nhap tu streamlit, vi URL_TU_TD_GUI la URL gui qua nen ko chac da duoc kiem tra hop le hay chua, con URL1 thi do nguoi dung nhap vao nen chac chan da kiem tra roi
    else:
        url_yt="" # ghi dai ma thoi de ko loi

    if 'https://' in url_yt:
    ########################        

        # BUOC 1 : LAY info BANG HAM tget_info(url)
        # ROI tu info tim va lay url cua json3 cua 
        # subtitles/automatic_captions ung voi lang en/en_GB/vi
        #------------------------------------------ 
        info = tget_info(url_yt)

        if info==None:
            st.write(':red[No info, stop here.]')
            st.stop()
        # co info roi thi moi lam tiep, neu ko co info thi da stop roi nen ko can else

        # TH 1 voi info da co -----
        if ((URL1 != "" and URL_TU_TD_GUI == "") or (URL1 == "" and URL_TU_TD_GUI != "")) and lamchon == 'subtitles':
            # luu cac tt can thiet
            video_id = info['id']
            video_title = info['title']
            video_duration_m = round(info['duration']/60,0)
            video_language = info['language'] if 'language' in info else 'unknown'
            st.write('0. :red[Language detected by yt-dlp : ]', video_language)

            # lay sub_lang_json3url (url cua phu de json ung voi lang chon) 
            # chu y rang thu tu cac lang da test nhieu lan, phai nhu nay thi moi de thanh cong
            # neu video_lang_source khac en thi nen dich qua tieng Anh
            #list_lang = ['en','en-US','en-GB','vi','vi-VN']
            if langchon == '.':
                langchon = video_language
            #list_lang = [langchon]
            sub_lang_json3url = None
            if 'subtitles' in info and info['subtitles'] != {}:
                sub = info['subtitles']
                #for lang in list_lang:
                if langchon in sub and sub_lang_json3url==None:
                    sub_lang_json3url = sub[langchon][0]['url']
                    kq = lay_datajso0n3(sub_lang_json3url)
                    if kq==True:
                        video_lang_source = langchon
                        #break
                    else:
                        sub_lang_json3url=None

            # neu van chua co thi tim lay trong automatic_captions
            if sub_lang_json3url == None:
                if 'automatic_captions' in info and info['automatic_captions'] != {}:
                    sub = info['automatic_captions']
                    #for lang in list_lang:
                    if langchon in sub and sub_lang_json3url==None:
                        sub_lang_json3url = sub[langchon][0]['url']
                        kq = lay_datajso0n3(sub_lang_json3url)
                        if kq==True:
                            video_lang_source = langchon
                            #break
                        else:
                            sub_lang_json3url=None

            # neu van chua co thi thong bao No va stop viec tim
            if sub_lang_json3url == None:
                st.write("No sub_lang_json3url !!")
                st.stop()

            # neu co thi tiep tuc tai xuong json3text tu sub_lang_json3url da tim duoc
            data=None
            try:
                response = requests.get(sub_lang_json3url)
                #st.write(response.text)
                datajson3 = response.json()
            except:
                st.write(":red[Getting for data json3 not succeed !]")
                st.stop()

            # neu chua stop tuc la lay datajson3 thanh cong, nen chuyen doi qua subtiles json
            subtitles = json3_to_segments(datajson3)
            #st.write(subtitles)
            # Cac thong tin day du :
            st.write('1. :blue[Url of yt video : ]', url_yt)
            st.write('2. :green[Id of yt video : ]', video_id)
            st.write('3. :blue[Title of yt video : ]', video_title)
            st.write('4. :green[Duration(m) of yt video : ]', video_duration_m)
            st.write('5. :blue[Source voice of yt video  : ]', video_lang_source)

            #Sua lai subtitles mot ti
            for item in subtitles:
                item['text'] = re.sub(">>", "", item['text'])
                item['text'] = re.sub(r"\[.*?\]", "", item['text'])
            
            
            # BUOC 3 : Gui subtitles len github de save vao thu muc Subs tren do
            #-------------------------------------------------------------------
            #Gui subtitles len github de save vao thu muc Subs tren do
            kq = tsend_to_gihub(subtitles,video_id)
            #st.write(subtitles, lang, id_video)
            st.write('6. :red[Ket qua gui Subs len Github: ]',video_id,kq)
    

            # BUOC 4 : Lap HTML_CODE DE HIEN THI WEB
            #----------------------------------------------------------
            html_code = lap_html_code(video_id, video_title, subtitles)

            # Hiển thị html_code trong Streamlit
            tieuDeTrangChinh.empty()
            aboutApp.empty()
            with aboutApp.container():
                st.components.v1.html(html_code, height=900, scrolling=True )

        # TH 2 voi info da co -----
        elif URL1 != "" and URL_TU_TD_GUI == "" and lamchon == 'chanelUrl':
            st.write(":red[channel_url : ]", info['channel_url'])
            # 1. Lấy JSON từ GitHub
            source_data = fetch_json_from_github()
            #tao item moi va listvideos de gui github
            itemnew, lvideosnew = get_videos_from_channel(info['channel_id'], len(source_data))
            source_data.append(itemnew)

            st.write(source_data)
            st.write(lvideosnew)
            
            # 2. Xử lý để tạo 2 file JSON mới
            # (Bạn thay logic xử lý theo nhu cầu)
            output1 = source_data
            output2 = lvideosnew

            # Tên file JSON sẽ tạo
            OUTPUT_FILE_1 = "Jschude/js_titleIdUrl_chude.json"
            OUTPUT_FILE_2 = f"Jschude/{info['channel_id']}.json"

            # 3. Upload 2 file JSON lên GitHub
            upload_to_github(OUTPUT_FILE_1, output1, commit_message="Add output1.json generated by Streamlit server")
            # OUTPUT_FILE_1 la gia tri truyen vao path_in_repo
            # output1 la gia tri truyen vao content_dict
            upload_to_github(OUTPUT_FILE_2, output2, commit_message="Add output2.json generated by Streamlit server")


            print("Đã tạo và upload 2 file JSON thành công!")