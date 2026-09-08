import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter # 득점/도움 개수 카운트를 위해 추가

# 웹사이트 전체 화면 넓게 쓰기 설정
st.set_page_config(page_title="학교 아침축구 리그", layout="wide")

st.title("우리 학교 아침축구 리그 스코어보드")

# --- 파일 경로 설정 ---
TEAMS_FILE = "teams_data.csv"
PLAYERS_FILE = "players_data.csv"
MATCHES_FILE = "matches_schedule.csv"

# --- 컬러 디자인 함수 ---
def style_team_colors(s):
    styles = []
    for val in s:
        if val == '지한풀':
            styles.append('background-color: #E6F2FF; color: #0047AB; font-weight: bold;') 
        elif val == 'U fc':
            styles.append('background-color: #FFE6E6; color: #B22222; font-weight: bold;') 
        elif val == '시체스터 원나이티드':
            styles.append('background-color: #F8F9FA; color: #333333; font-weight: bold;') 
        else:
            styles.append('')
    return styles

def get_color_dot(team_name):
    if team_name == '지한풀': 
        return '<span style="color:#0047AB;">●</span>'
    elif team_name == 'U fc': 
        return '<span style="color:#B22222;">●</span>'
    elif team_name == '시체스터 원나이티드': 
        return '<span style="color:#A9A9A9;">●</span>' 
    return ''

# --- 초기 데이터 자동 생성 및 로드 함수 ---
def load_data():
    if os.path.exists(TEAMS_FILE):
        teams_df = pd.read_csv(TEAMS_FILE)
    else:
        teams_df = pd.DataFrame({
            '팀명': ['지한풀', 'U fc', '시체스터 원나이티드'],
            '승': [0, 0, 0], '무': [0, 0, 0], '패': [0, 0, 0],
            '득점': [0, 0, 0], '실점': [0, 0, 0]
        })
        teams_df.to_csv(TEAMS_FILE, index=False)
        
    if os.path.exists(PLAYERS_FILE):
        players_df = pd.read_csv(PLAYERS_FILE)
    else:
        players_df = pd.DataFrame(
            columns=['이름', '소속팀', '포지션', '등번호', '골', '도움', '포인트']
        )
        players_df.to_csv(PLAYERS_FILE, index=False)

    if os.path.exists(MATCHES_FILE):
        matches_df = pd.read_csv(MATCHES_FILE)
    else:
        match_list = []
        start_date = datetime(2026, 9, 9) 
        end_date = datetime(2026, 11, 27)
        
        base_matchups = [
            ('지한풀', 'U fc'),
            ('U fc', '시체스터 원나이티드'),
            ('지한풀', '시체스터 원나이티드')
        ]
        match_times = ['07:40-07:55', '07:55-08:10', '08:10-08:25']
        
        curr = start_date
        match_id = 1
        day_idx = 0 
        
        while curr <= end_date:
            if curr.weekday() in [2, 4]: 
                if day_idx % 3 == 0:
                    daily_order = [0, 1, 2]
                elif day_idx % 3 == 1:
                    daily_order = [1, 2, 0]
                else:
                    daily_order = [2, 0, 1]
                    
                for i, m_idx in enumerate(daily_order):
                    t1, t2 = base_matchups[m_idx]
                    time_slot = match_times[i]
                    match_list.append({
                        '경기ID': match_id, '날짜': curr.strftime('%Y-%m-%d'), '시간': time_slot,
                        '홈팀': t1, '원정팀': t2, '홈팀점수': 0, '원정팀점수': 0,
                        '상태': '예정됨', '득점요약': '', '도움요약': ''
                    })
                    match_id += 1
                day_idx += 1 
            curr += timedelta(days=1)
            
        matches_df = pd.DataFrame(match_list)
        matches_df.to_csv(MATCHES_FILE, index=False)
        
    return teams_df, players_df, matches_df

df_teams, df_players, df_matches = load_data()

# --- 탭(메뉴) 만들기 ---
tab1, tab2, tab3, tab4 = st.tabs(["팀 순위표", "개인 랭킹", "경기 일정 및 결과", "관리자 설정"])

# --- TAB 1: 팀 순위표 ---
with tab1:
    st.header("현재 팀 순위")
    t_df = df_teams.copy()
    t_df['승점'] = (t_df['승'] * 3) + (t_df['무'] * 1)
    t_df['득실차'] = t_df['득점'] - t_df['실점']
    t_df = t_df.sort_values(by=['승점', '득실차', '득점'], ascending=[False, False, False]).reset_index(drop=True)
    t_df.index = t_df.index + 1  
    
    display_teams = t_df[['팀명', '승점', '승', '무', '패', '득점', '실점', '득실차']]
    styled_teams = display_teams.style.apply(style_team_colors, subset=['팀명'])
    st.dataframe(styled_teams, use_container_width=True)

# --- TAB 2: 개인 랭킹 ---
with tab2:
    st.header("선수 개인 기록 및 랭킹")
    if len(df_players) == 0:
        st.info("아직 등록된 선수가 없습니다. 관리자 탭에서 선수를 추가해주세요.")
    else:
        p_df = df_players.copy()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("득점왕 랭킹")
            top_scorers = p_df.sort_values(by='골', ascending=False)[['이름', '소속팀', '골']].head(5)
            top_scorers = top_scorers[top_scorers['골'] > 0].reset_index(drop=True)
            top_scorers.index = top_scorers.index + 1
            st.dataframe(top_scorers.style.apply(style_team_colors, subset=['소속팀']), use_container_width=True)
            
        with col2:
            st.subheader("도움왕 랭킹")
            top_assists = p_df.sort_values(by='도움', ascending=False)[['이름', '소속팀', '도움']].head(5)
            top_assists = top_assists[top_assists['도움'] > 0].reset_index(drop=True)
            top_assists.index = top_assists.index + 1
            st.dataframe(top_assists.style.apply(style_team_colors, subset=['소속팀']), use_container_width=True)
            
        with col3:
            st.subheader("포인트 랭킹 (골+도움)")
            top_points = p_df.sort_values(by='포인트', ascending=False)[['이름', '소속팀', '포인트']].head(5)
            top_points = top_points[top_points['포인트'] > 0].reset_index(drop=True)
            top_points.index = top_points.index + 1
            st.dataframe(top_points.style.apply(style_team_colors, subset=['소속팀']), use_container_width=True)
        
        st.divider()
        st.subheader("전체 선수 명단")
        all_players = p_df.sort_values(by='포인트', ascending=False).reset_index(drop=True)
        st.dataframe(all_players.style.apply(style_team_colors, subset=['소속팀']), use_container_width=True)

# --- TAB 3: 경기 일정 및 결과 ---
with tab3:
    st.header("전체 경기 일정 및 결과 (Matches)")
    
    sub_tab1, sub_tab2 = st.tabs(["날짜별 경기 보기 (달력)", "전체 매치 리스트"])
    
    with sub_tab1:
        st.write("원하시는 **경기 날짜**를 선택하고 **경기를 클릭**하여 스코어와 명단을 확인하세요.")
        all_dates = sorted(df_matches['날짜'].unique())
        if all_dates:
            selected_date = st.selectbox("날짜 선택", all_dates)
            day_matches = df_matches[df_matches['날짜'] == selected_date]
            
            for idx, row in day_matches.iterrows():
                h_team = row['홈팀']
                a_team = row['원정팀']
                status_icon = "✅" if row['상태'] == '종료됨' else "⏳"
                expander_title = f"{status_icon} [{row['시간']}] {h_team} vs {a_team}"
                
                # 경기를 클릭(터치)하면 열리는 상세 패널
                with st.expander(expander_title):
                    if row['상태'] == '종료됨':
                        # 1. 최상단: 양 팀 스코어보드
                        st.markdown(f"""
                        <div style='text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                            <h2 style='margin: 0;'>{get_color_dot(h_team)} {h_team} <span style='font-size: 1.5em; margin: 0 20px; color: #333;'>{row['홈팀점수']} : {row['원정팀점수']}</span> {a_team} {get_color_dot(a_team)}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 해당 경기의 득점/도움 기록 분석 (이름 쉼표 단위 분리)
                        scorers_list = [s.strip() for s in str(row['득점요약']).split(',')] if pd.notna(row['득점요약']) and row['득점요약'] not in ['', '기록 없음'] else []
                        assisters_list = [s.strip() for s in str(row['도움요약']).split(',')] if pd.notna(row['도움요약']) and row['도움요약'] not in ['', '기록 없음'] else []
                        
                        goal_counts = Counter(scorers_list)
                        assist_counts = Counter(assisters_list)
                        
                        # 2. 좌우: 팀별 선수 명단
                        col_left, col_right = st.columns(2)
                        h_players = df_players[df_players['소속팀'] == h_team].sort_values(by=['등번호', '이름'])
                        a_players = df_players[df_players['소속팀'] == a_team].sort_values(by=['등번호', '이름'])
                        
                        with col_left:
                            st.markdown(f"#### 🛡️ {h_team} 출전 명단")
                            if len(h_players) == 0:
                                st.caption("등록된 선수가 없습니다.")
                            for _, p_row in h_players.iterrows():
                                p_name = p_row['이름']
                                g_count = goal_counts.get(p_name, 0)
                                a_count = assist_counts.get(p_name, 0)
                                stat_emojis = ("⚽" * g_count) + ("👟" * a_count)
                                st.write(f"**{p_row['등번호']}** {p_name} {stat_emojis}")
                                
                        with col_right:
                            st.markdown(f"#### 🛡️ {a_team} 출전 명단")
                            if len(a_players) == 0:
                                st.caption("등록된 선수가 없습니다.")
                            for _, p_row in a_players.iterrows():
                                p_name = p_row['이름']
                                g_count = goal_counts.get(p_name, 0)
                                a_count = assist_counts.get(p_name, 0)
                                stat_emojis = ("⚽" * g_count) + ("👟" * a_count)
                                st.write(f"**{p_row['등번호']}** {p_name} {stat_emojis}")
                    else:
                        # 아직 진행되지 않은 경기
                        st.markdown(f"""
                        <div style='text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                            <h2 style='margin: 0;'>{get_color_dot(h_team)} {h_team} <span style='font-size: 1.2em; margin: 0 20px; color: #888;'>VS</span> {a_team} {get_color_dot(a_team)}</h2>
                            <p style='color: #888; margin-top: 10px;'>아직 치러지지 않은 경기입니다.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_left, col_right = st.columns(2)
                        h_players = df_players[df_players['소속팀'] == h_team].sort_values(by=['등번호', '이름'])
                        a_players = df_players[df_players['소속팀'] == a_team].sort_values(by=['등번호', '이름'])
                        
                        with col_left:
                            st.markdown(f"#### 🛡️ {h_team} 예상 명단")
                            for _, p_row in h_players.iterrows():
                                st.write(f"**{p_row['등번호']}** {p_row['이름']}")
                        with col_right:
                            st.markdown(f"#### 🛡️ {a_team} 예상 명단")
                            for _, p_row in a_players.iterrows():
                                st.write(f"**{p_row['등번호']}** {p_row['이름']}")
            
    with sub_tab2:
        st.write("시즌 전체의 경기 결과와 예정된 매치 목록입니다.")
        display_match_list = df_matches[['날짜', '시간', '홈팀', '원정팀', '홈팀점수', '원정팀점수', '상태', '득점요약']]
        styled_match_list = display_match_list.style.apply(style_team_colors, subset=['홈팀']).apply(style_team_colors, subset=['원정팀'])
        st.dataframe(styled_match_list, use_container_width=True)

# --- TAB 4: 관리자 설정 ---
with tab4:
    st.header("관리자 설정 및 경기 결과 입력")
    password_input = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if password_input == "OMS26":
        st.success("관리자 권한이 확인되었습니다!")
        st.divider()
        
        # 1. 통합 경기 결과 및 스탯 입력 시스템
        st.subheader("경기 결과 및 스탯 통합 입력")
        match_options = df_matches.apply(lambda r: f"[{r['날짜']} {r['시간']}] {r['홈팀']} vs {r['원정팀']} ({r['상태']})", axis=1).tolist()
        selected_match_str = st.selectbox("결과를 입력할 경기 선택", match_options)
        
        match_idx = match_options.index(selected_match_str)
        target_match = df_matches.iloc[match_idx]
        
        with st.form("match_result_form"):
            h_team = target_match['홈팀']
            a_team = target_match['원정팀']
            
            st.markdown(f"### [{target_match['시간']}] {get_color_dot(h_team)} {h_team} vs {get_color_dot(a_team)} {a_team}", unsafe_allow_html=True)
            
            col_score1, col_score2 = st.columns(2)
            with col_score1:
                home_score = st.number_input(f"{h_team} 득점", min_value=0, step=1, value=int(target_match['홈팀점수']))
            with col_score2:
                away_score = st.number_input(f"{a_team} 득점", min_value=0, step=1, value=int(target_match['원정팀점수']))
            
            st.write("---")
            st.write("**선수 기록 입력 (선택사항)**")
            player_names = df_players['이름'].tolist() if len(df_players) > 0 else []
            
            scorer_1 = st.selectbox("골 넣은 선수 (1)", ["선택 안 함"] + player_names, key="sc1")
            assister_1 = st.selectbox("도움 준 선수 (1)", ["선택 안 함"] + player_names, key="as1")
            scorer_2 = st.selectbox("골 넣은 선수 (2)", ["선택 안 함"] + player_names, key="sc2")
            assister_2 = st.selectbox("도움 준 선수 (2)", ["선택 안 함"] + player_names, key="as2")
            
            submit_match_result = st.form_submit_button("경기 결과 및 스탯 최종 반영하기")
            
            if submit_match_result:
                h_team_idx = df_teams[df_teams['팀명'] == h_team].index[0]
                a_team_idx = df_teams[df_teams['팀명'] == a_team].index[0]
                
                df_matches.at[match_idx, '홈팀점수'] = home_score
                df_matches.at[match_idx, '원정팀점수'] = away_score
                df_matches.at[match_idx, '상태'] = '종료됨'
                
                df_teams.at[h_team_idx, '득점'] += home_score
                df_teams.at[h_team_idx, '실점'] += away_score
                df_teams.at[a_team_idx, '득점'] += away_score
                df_teams.at[a_team_idx, '실점'] += home_score
                
                if home_score > away_score:
                    df_teams.at[h_team_idx, '승'] += 1
                    df_teams.at[a_team_idx, '패'] += 1
                elif home_score < away_score:
                    df_teams.at[a_team_idx, '승'] += 1
                    df_teams.at[h_team_idx, '패'] += 1
                else:
                    df_teams.at[h_team_idx, '무'] += 1
                    df_teams.at[a_team_idx, '무'] += 1
                
                scorers_recorded = []
                assists_recorded = []
                
                for sc, ast in [(scorer_1, assister_1), (scorer_2, assister_2)]:
                    if sc != "선택 안 함":
                        p_idx = df_players[df_players['이름'] == sc].index[0]
                        df_players.at[p_idx, '골'] += 1
                        df_players.at[p_idx, '포인트'] = df_players.at[p_idx, '골'] + df_players.at[p_idx, '도움']
                        scorers_recorded.append(sc)
                    if ast != "선택 안 함":
                        p_idx = df_players[df_players['이름'] == ast].index[0]
                        df_players.at[p_idx, '도움'] += 1
                        df_players.at[p_idx, '포인트'] = df_players.at[p_idx, '골'] + df_players.at[p_idx, '도움']
                        assists_recorded.append(ast)
                
                df_matches.at[match_idx, '득점요약'] = ", ".join(scorers_recorded) if scorers_recorded else "기록 없음"
                df_matches.at[match_idx, '도움요약'] = ", ".join(assists_recorded) if assists_recorded else "기록 없음"
                
                df_teams.to_csv(TEAMS_FILE, index=False)
                df_players.to_csv(PLAYERS_FILE, index=False)
                df_matches.to_csv(MATCHES_FILE, index=False)
                
                st.success("경기 결과와 선수 스탯이 성공적으로 반영되었습니다!")
                st.rerun()

        st.divider()
        
        # 2. 선수 관리 (등록 및 정보 수정)
        st.subheader("선수 관리 (등록 및 정보 수정)")
        player_tab1, player_tab2 = st.tabs(["신규 선수 등록", "기존 선수 정보 수정"])
        
        with player_tab1:
            with st.form("add_player_form"):
                new_name = st.text_input("선수 이름")
                new_team = st.selectbox("소속팀", df_teams['팀명'].tolist())
                new_position = st.selectbox("포지션", ["FW (공격수)", "MF (미드필더)", "DF (수비수)", "GK (골키퍼)"])
                new_number = st.number_input("등번호", min_value=1, max_value=99, step=1)
                
                submit_player = st.form_submit_button("선수 등록하기")
                if submit_player and new_name:
                    new_row = pd.DataFrame([{
                        '이름': new_name, '소속팀': new_team, '포지션': new_position, 
                        '등번호': new_number, '골': 0, '도움': 0, '포인트': 0
                    }])
                    df_players = pd.concat([df_players, new_row], ignore_index=True)
                    df_players.to_csv(PLAYERS_FILE, index=False)
                    st.success(f"{new_name} 선수가 등록되었습니다!")
                    st.rerun()

        with player_tab2:
            if len(df_players) > 0:
                with st.form("edit_player_form"):
                    target_player = st.selectbox("정보를 수정할 선수 선택", df_players['이름'].tolist())
                    p_row = df_players[df_players['이름'] == target_player].iloc[0]
                    
                    edit_name = st.text_input("수정할 선수 이름", value=str(p_row['이름']))
                    edit_team = st.selectbox("소속팀 변경", df_teams['팀명'].tolist(), index=df_teams['팀명'].tolist().index(p_row['소속팀']) if p_row['소속팀'] in df_teams['팀명'].tolist() else 0)
                    
                    pos_list = ["FW (공격수)", "MF (미드필더)", "DF (수비수)", "GK (골키퍼)"]
                    pos_idx = pos_list.index(p_row['포지션']) if p_row['포지션'] in pos_list else 0
                    edit_position = st.selectbox("포지션 변경", pos_list, index=pos_idx)
                    edit_number = st.number_input("등번호 변경", min_value=1, max_value=99, step=1, value=int(p_row['등번호']))
                    
                    submit_edit = st.form_submit_button("선수 정보 수정 반영")
                    if submit_edit and edit_name:
                        p_idx = df_players[df_players['이름'] == target_player].index[0]
                        df_players.at[p_idx, '이름'] = edit_name
                        df_players.at[p_idx, '소속팀'] = edit_team
                        df_players.at[p_idx, '포인트' ] = df_players.at[p_idx, '골'] + df_players.at[p_idx, '도움']
                        df_players.at[p_idx, '포지션'] = edit_position
                        df_players.at[p_idx, '등번호'] = edit_number
                        df_players.to_csv(PLAYERS_FILE, index=False)
                        st.success(f"{target_player} 선수의 정보가 수정되었습니다!")
                        st.rerun()
            else:
                st.info("등록된 선수가 없습니다. 먼저 선수를 등록해주세요.")

        st.divider()
        
        # 3. 팀 이름 변경하기
        st.subheader("팀 이름 변경하기")
        target_team = st.selectbox("이름을 바꿀 팀 선택", df_teams['팀명'].tolist(), key="rename_target")
        new_team_name = st.text_input("새로운 팀 이름 입력")
        
        if st.button("팀 이름 변경 적용"):
            if new_team_name and new_team_name not in df_teams['팀명'].tolist():
                team_idx = df_teams[df_teams['팀명'] == target_team].index[0]
                df_teams.at[team_idx, '팀명'] = new_team_name
                df_matches.loc[df_matches['홈팀'] == target_team, '홈팀'] = new_team_name
                df_matches.loc[df_matches['원정팀'] == target_team, '원정팀'] = new_team_name
                if len(df_players) > 0:
                    df_players.loc[df_players['소속팀'] == target_team, '소속팀'] = new_team_name
                
                df_teams.to_csv(TEAMS_FILE, index=False)
                df_players.to_csv(PLAYERS_FILE, index=False)
                df_matches.to_csv(MATCHES_FILE, index=False)
                
                st.success(f"팀 이름이 '{target_team}'에서 '{new_team_name}'(으)로 변경되었습니다!")
                st.rerun()
            else:
                st.error("이미 존재하는 팀명이거나 올바른 이름을 입력해주세요.")
                
    elif password_input == "":
        st.info("관리자 기능을 이용하려면 비밀번호를 입력하세요.")
    else:
        st.error("비밀번호가 틀렸습니다. 올바른 비밀번호를 입력해주세요.")
