import subprocess
import datetime
import os
from collections import defaultdict

def get_git_logs():
    """최근 하루 동안의 git 로그를 가져옵니다."""
    command = [
        'git', 'log', '--since="1 day ago"',
        '--pretty=format:%an|%s'
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error getting git log: {result.stderr}")
        return None
    return result.stdout.strip().split('\n')

def group_logs_by_author(logs):
    """로그를 작성자별로 그룹화합니다."""
    grouped_logs = defaultdict(list)
    if not logs or (len(logs) == 1 and logs[0] == ''):
        return grouped_logs
        
    for log in logs:
        try:
            author, message = log.split('|', 1)
            grouped_logs[author.strip()].append(message.strip())
        except ValueError:
            # 파이프가 없는 로그 라인은 무시합니다.
            print(f"Skipping malformed log line: {log}")
            continue
    return grouped_logs

def generate_markdown(grouped_logs):
    """작성자별 로그를 마크다운 형식으로 변환합니다."""
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 중복 제거를 위해 set 사용
    total_contributors = set(grouped_logs.keys())
    total_commits = sum(len(messages) for messages in grouped_logs.values())

    md_content = f"# Daily Task Summary - {today_str}\n\n"
    md_content += "## 📈 Summary\n\n"
    md_content += f"- **Total Commits:** {total_commits}\n"
    md_content += f"- **Total Contributors:** {len(total_contributors)}\n\n"
    md_content += "---\n\n"
    md_content += "## 🧑‍💻 Work Details by Member\n\n"

    for author, messages in grouped_logs.items():
        md_content += f"### {author}\n"
        for msg in messages:
            md_content += f"- {msg}\n"
        md_content += "\n"
        
    return md_content

def main():
    """메인 실행 함수"""
    logs = get_git_logs()
    if logs is None:
        return

    grouped_logs = group_logs_by_author(logs)
    
    if not grouped_logs:
        print("No new commits found in the last day.")
        return

    markdown_content = generate_markdown(grouped_logs)
    
    # 출력 디렉토리 설정
    output_dir = os.path.join('docs', 'dts')
    os.makedirs(output_dir, exist_ok=True)

    # 파일명 생성 (YYMMDD_dts.md)
    filename_date = datetime.datetime.now().strftime('%y%m%d')
    filename = f"{filename_date}_dts.md"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Successfully created daily task summary: {filepath}")
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}")

if __name__ == "__main__":
    main()