#!/usr/bin/env python3

from logging import basicConfig, getLogger, INFO
from flask import Flask, request, jsonify
from html import escape
from requests import get, post
from os import environ
import config

from telegram.ext import CommandHandler, Updater


server = Flask(__name__)

basicConfig(level=INFO)
log = getLogger()

ENV = bool(environ.get('ENV', False))

if ENV:
    BOT_TOKEN = environ.get('BOT_TOKEN', None)
    PROJECT_NAME = environ.get('PROJECT_NAME', None)
    ip_addr = environ.get('APP_URL', None)
else:
    BOT_TOKEN = config.BOT_TOKEN
    PROJECT_NAME = config.PROJECT_NAME
    ip_addr = get('https://api.ipify.org').text

updater = Updater(token=BOT_TOKEN, workers=1)
dispatcher = updater.dispatcher

print("If you need more information contact @YorktownEagleUnion")


def start(_bot, update):
    """/start message for bot"""
    message = update.effective_message
    message.reply_text(
        f"This is the Updates watcher for {PROJECT_NAME}\nYou are not authorized to be here",
        parse_mode="markdown")


start_handler = CommandHandler("start", start)

dispatcher.add_handler(start_handler)
updater.start_polling()

TG_BOT_API = f'https://api.telegram.org/bot{BOT_TOKEN}/'
checkbot = get(TG_BOT_API + "getMe").json()
if not checkbot['ok']:
    log.error("Invalid Token!")
    exit(1)
else:
    username = checkbot['result']['username']
    log.info(
        f"logged in as @{username}")


def post_tg(chat, message, parse_mode):
    """Send message to desired group"""
    response = post(
        TG_BOT_API + "sendMessage",
        params={
            "chat_id": chat,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True}).json()
    return response


def reply_tg(chat, message_id, message, parse_mode):
    """reply to message_id"""
    response = post(
        TG_BOT_API + "sendMessage",
        params={
            "chat_id": chat,
            "reply_to_message_id": message_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True}).json()
    return response


@server.route("/<groupid>", methods=['GET', 'POST'])
def git_api(groupid):
    """Requests to api.github.com"""
    data = request.json
    if not data:
        return f"<b>Add this url:</b> {ip_addr}/{groupid} to webhooks of the project"

    if data.get('hook'):
        repo_url = data['repository']['html_url']
        repo_name = data['repository']['name']
        sender_url = data['sender']['html_url']
        sender_name = data['sender']['login']
        comments = data['comment']['body']
        commits_data = len(data['commits']
        comment_url = data['comment']['html_url']
        issue_no = data['issue']['number']
        issue_title = data['issue']['title']
        issue = data['issue']['body']
        issue_url = data['issue']['html_url']
        pr_state = data['pull_request']['state']
        response = post_tg(
                groupid,
                f"🙌 Successfully set webhook for <a href='{repo_url}'>{repo_name}</a> by <a href='{sender_url}'>{sender_name}</a>!",
                "html"
            )
        return response

    if data.get('commits'):
        commits_text = ""
        rng = commits_data
        if rng > 10:
            rng = 10
        for x in range(rng):
            commit = data['commits'][x]
            if len(escape(commit['message'])) > 300:
                commit_msg = escape(commit['message']).split("\n")[0]
            else:
                commit_msg = escape(commit['message'])
            commits_text += f"{commit_msg}\n<a href='{commit['url']}'>{commit['id'][:7]}</a> - {commit['author']['name']} {escape('<')}{commit['author']['email']}{escape('>')}\n\n"
            if len(commits_text) > 1000:
                text = f"""✨ <b>{escape(repo_name)}</b> - New {commits_data} commits ({escape(data['ref'].split('/')[-1])})
{commits_text}
"""
                response = post_tg(groupid, text, "html")
                commits_text = ""
        if not commits_text:
            return jsonify({"ok": True, "text": "Commits text is none"})
        ref_data = escape(data['ref'].split('/')[-1])
        text = f"""✨ <b>{repo_name}</b> - New {commits_data} commits ({ref_data})
{commits_text}
"""
        if commits_data > 10:
            text += f"\n\n<i>And {commits_data - 10} other commits</i>"
        response = post_tg(groupid, text, "html")
        return response

    if data.get('issue'):
        if data.get('comment'):
            text = f"""💬 New comment: <b>{escape(repo_name)}</b>
{escape(comments)}

<a href='{comment_url}'>Issue #{issue_no}</a>
"""
            response = post_tg(groupid, text, "html")
            return response
        text = f"""🚨 New {data['action']} issue for <b>{escape(repo_name)}</b>
<b>{escape(issue_title)}</b>
{escape(issue)}

<a href='{issue_url}'>issue #{issue_no}</a>
"""
        response = post_tg(groupid, text, "html")
        return response

    if data.get('pull_request'):
        if data.get('comment'):
            text = f"""❗ There is a new pull request for <b>{escape(repo_name)}</b> ({pr_state})
{escape(comments)}

<a href='{comment_url}'>Pull request #{issue_no}</a>
"""
            response = post_tg(groupid, text, "html")
            return response
        text = f"""❗  New {data['action']} pull request for <b>{escape(repo_name)}</b>
<b>{escape(data['pull_request']['title'])}</b> ({pr_state})
{escape(data['pull_request']['body'])}

<a href='{data['pull_request']['html_url']}'>Pull request #{data['pull_request']['number']}</a>
"""
        response = post_tg(groupid, text, "html")
        return response

    if data.get('forkee'):
        response = post_tg(
            groupid,
            f"🍴 <a href='{sender_url}'>{sender_name}</a> forked <a href='{repo_url}'>{repo_name}</a>!\nTotal forks now are {data['repository']['forks_count']}",
            "html")
        return response

    if data.get('action'):

        if data.get('action') == "published" and data.get('release'):
            text = f"<a href='{sender_url}'>{sender_name}</a> {data['action']} <a href='{repo_url}'>{repo_name}</a>!"
            text += f"\n\n<b>{data['release']['name']}</b> ({data['release']['tag_name']})\n{data['release']['body']}\n\n<a href='{data['release']['tarball_url']}'>Download tar</a> | <a href='{data['release']['zipball_url']}'>Download zip</a>"
            response = post_tg(groupid, text, "html")
            return response

        if data.get('action') == "started":
            text = f"🌟 <a href='{sender_url}'>{sender_name}</a> gave a star to <a href='{repo_url}'>{repo_name}</a>!\nTotal stars are now {data['repository']['stargazers_count']}"
            response = post_tg(groupid, text, "html")
            return response

        if data.get('action') == "edited" and data.get('release'):
            text = f"<a href='{sender_url}'>{sender_name}</a> {data['action']} <a href='{repo_url}'>{repo_name}</a>!"
            text += f"\n\n<b>{data['release']['name']}</b> ({data['release']['tag_name']})\n{data['release']['body']}\n\n<a href='{data['release']['tarball_url']}'>Download tar</a> | <a href='{data['release']['zipball_url']}'>Download zip</a>"
            response = post_tg(groupid, text, "html")
            return response

        if data.get('action') == "created":
            return jsonify({"ok": True, "text": "Pass trigger for created"})

        response = post_tg(
            groupid,
            f"<a href='{sender_url}'>{sender_name}</a> {data['action']} <a href='{repo_url}'>{repo_name}</a>!",
            "html")
        return response

    if data.get('ref_type'):
        response = post_tg(
            groupid,
            f"A new {data['ref_type']} on <a href='{repo_url}'>{repo_name}</a> was created by <a href='{sender_url}'>{sender_name}</a>!",
            "html")
        return response

    if data.get('created'):
        response = post_tg(groupid,
            f"Branch {data['ref'].split('/')[-1]} <b>{data['ref'].split('/')[-2]}</b> on <a href='{repo_url}'>{repo_name}</a> was created by <a href='{sender_url}'>{sender_name}</a>!",
                           "html")
        return response

    if data.get('deleted'):
        response = post_tg(groupid,
                           f"Branch {data['ref'].split('/')[-1]} <b>{data['ref'].split('/')[-2]}</b> on <a href='{repo_url}'>{repo_name}</a> was deleted by <a href='{sender_url}'>{sender_name}</a>!",
                           "html")
        return response

    if data.get('forced'):
        response = post_tg(groupid,
                           f"Branch {data['ref'].split('/')[-1]} <b>{data['ref'].split('/')[-2]}</b> on <a href='{repo_url}'>{repo_name}</a> was forced by <a href='{sender_url}'>{sender_name}</a>!",
                           "html")
        return response

    if data.get('pages'):
        text = f"<a href='{repo_url}'>{repo_name}</a> wiki pages were updated by <a href='{sender_url}'>{sender_name}</a>!\n\n"
        for x in data['pages']:
            summary = ""
            if x['summary']:
                summary = f"{x['summary']}\n"
            text += f"📝 <b>{escape(x['title'])}</b> ({x['action']})\n{summary}<a href='{x['html_url']}'>{x['page_name']}</a> - {x['sha'][:7]}"
            if len(data['pages']) >= 2:
                text += "\n=====================\n"
            response = post_tg(groupid, text, "html")
        return response

    if data.get('context'):
        if data.get('state') == "pending":
            emo = "⏳"
        elif data.get('state') == "success":
            emo = "✔️"
        elif data.get('state') == "failure":
            emo = "❌"
        else:
            emo = "🌀"
        response = post_tg(
            groupid,
            f"{emo} <a href='{data['target_url']}'>{data['description']}</a> on <a href='{repo_url}'>{repo_name}</a> by <a href='{sender_url}'>{sender_name}</a>!\nLatest commit:\n<a href='{data['commit']['commit']['url']}'>{escape(data['commit']['commit']['message'])}</a>",
            "html")
        return response

    url = deldog(data)
    response = post_tg(
        groupid,
        f"🚫 Undetected response: {url}",
        "markdown")
    return response


def deldog(data):
    """Pasing the stings to del.dog"""
    BASE_URL = 'https://del.dog'
    r = post(f'{BASE_URL}/documents', data=str(data).encode('utf-8'))
    if r.status_code == 404:
        r.raise_for_status()
    res = r.json()
    if r.status_code != 200:
        r.raise_for_status()
    key = res['key']
    if res['isUrl']:
        reply = f'DelDog URL: {BASE_URL}/{key}\nYou can view stats, etc. [here]({BASE_URL}/v/{key})'
    else:
        reply = f'{BASE_URL}/{key}'
    return reply


if __name__ == "__main__":
    # We can't use port 80 due to the root access requirement.
    port = int(environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)
