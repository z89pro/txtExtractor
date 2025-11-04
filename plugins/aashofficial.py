#  MIT License
#
#  Copyright (c) 2019-present Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE
#  Code edited By Cryptostark

import urllib
import urllib.parse
import requests
import json
import subprocess
from pyrogram.types.messages_and_media import message
import helper
from pyromod import listen
from pyrogram.types import Message
import tgcrypto
import pyrogram
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import time
from pyrogram.types import User, Message
from p_bar import progress_bar
from subprocess import getstatusoutput
import logging
import os
import sys
import re
from pyrogram import Client as bot
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode

def decode_aash(encrypted_url):
    """Decode encrypted URLs for aashofficial platform"""
    try:
        # This is a placeholder - actual decryption logic would need to be reverse engineered
        # from the aashofficial platform's JavaScript/mobile app
        key = "aashofficial2023".encode("utf8")[:16]  # Adjust based on actual key
        iv = "1234567890123456".encode("utf8")  # Adjust based on actual IV
        
        ciphertext = bytearray.fromhex(b64decode(encrypted_url.encode()).hex())
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        url = plaintext.decode('utf-8')
        return url
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_url

@bot.on_message(filters.command(["aashofficial"]))
async def aashofficial_extractor(bot: Client, m: Message):
    """Extract content from aashofficial.classx.co.in"""
    s = requests.Session()
    global cancel
    cancel = False
    
    editable = await m.reply_text(
        "🔐 **Aash Official Extractor**\n\n"
        "Send **ID & Password** in this format:\n"
        "**ID*Password**\n\n"
        "Example: `student123*mypassword`"
    )
    
    # API endpoints for aashofficial
    login_url = "https://aashofficial.classx.co.in/post/userLogin"
    
    headers = {
        "Auth-Key": "appxapi",
        "User-Id": "-2", 
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1"
    }
    
    try:
        # Get user credentials
        input1: Message = await bot.listen(editable.chat.id)
        raw_text = input1.text
        
        if "*" not in raw_text:
            await editable.edit("❌ **Error:** Please use the correct format: ID*Password")
            return
            
        credentials = {"email": "", "password": ""}
        credentials["email"] = raw_text.split("*")[0].strip()
        credentials["password"] = raw_text.split("*")[1].strip()
        await input1.delete(True)
        
        # Validate credentials
        if not credentials["email"] or not credentials["password"]:
            await editable.edit("❌ **Error:** Email and password cannot be empty")
            return
        
        await editable.edit("🔄 **Logging in...**")
        
        # Login request
        scraper = cloudscraper.create_scraper()
        response = scraper.post(login_url, data=credentials, headers=headers)
        
        if response.status_code != 200:
            await editable.edit(f"❌ **Login Failed:** Server returned status {response.status_code}")
            return
            
        try:
            login_data = response.json()
        except json.JSONDecodeError:
            await editable.edit("❌ **Error:** Invalid response from server")
            return
            
        if "data" not in login_data or "userid" not in login_data["data"]:
            await editable.edit("❌ **Login Failed:** Invalid credentials or server error")
            return
            
        userid = login_data["data"]["userid"]
        token = login_data["data"]["token"]
        
        # Update headers with authentication
        auth_headers = {
            "Host": "aashofficial.classx.co.in",
            "Client-Service": "Appx", 
            "Auth-Key": "appxapi",
            "User-Id": userid,
            "Authorization": token
        }
        
        await editable.edit("✅ **Login Successful!**\n🔄 **Fetching courses...**")
        
        # Get user courses
        courses_url = f"https://aashofficial.classx.co.in/get/mycourse?userid={userid}"
        courses_response = s.get(courses_url, headers=auth_headers)
        
        if courses_response.status_code != 200:
            await editable.edit("❌ **Error:** Failed to fetch courses")
            return
            
        courses_data = courses_response.json()
        
        if "data" not in courses_data or not courses_data["data"]:
            await editable.edit("❌ **No courses found for this account**")
            return
            
        # Display available courses
        course_list = ""
        for course in courses_data["data"]:
            course_name = course.get("course_name", "Unknown Course")
            course_id = course.get("id", "N/A")
            course_list += f"```{course_id}``` - **{course_name}**\n\n"
            
        await editable.edit(
            f"📚 **Available Courses:**\n\n{course_list}"
            f"📝 **Send Course ID to extract content**"
        )
        
        # Get course selection
        input2: Message = await bot.listen(editable.chat.id)
        course_id = input2.text.strip()
        await input2.delete(True)
        
        if not course_id.isdigit():
            await editable.edit("❌ **Error:** Please send a valid course ID (numbers only)")
            return
            
        await editable.edit("🔄 **Extracting course content...**")
        
        # Get course details and subjects
        subjects_url = f"https://aashofficial.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={course_id}"
        subjects_response = scraper.get(subjects_url, headers=auth_headers)
        
        if subjects_response.status_code != 200:
            await editable.edit("❌ **Error:** Failed to fetch course subjects")
            return
            
        subjects_data = subjects_response.json()
        
        if "data" not in subjects_data or not subjects_data["data"]:
            await editable.edit("❌ **No subjects found for this course**")
            return
            
        # Display subjects
        subject_list = ""
        subject_ids = ""
        for subject in subjects_data["data"]:
            subject_name = subject.get("subject_name", "Unknown Subject")
            subject_id = subject.get("subjectid", "N/A")
            subject_list += f"```{subject_id}``` - **{subject_name}**\n\n"
            subject_ids += f"{subject_id}&"
            
        await editable.edit(
            f"📖 **Available Subjects:**\n\n{subject_list}"
            f"📝 **Send Subject IDs** (format: 1&2&3) or copy this for all:\n"
            f"```{subject_ids.rstrip('&')}```"
        )
        
        # Get subject selection
        input3: Message = await bot.listen(editable.chat.id)
        selected_subjects = input3.text.strip()
        await input3.delete(True)
        
        await editable.edit("🔄 **Extracting video links...**")
        
        # Extract videos from selected subjects
        course_name = courses_data["data"][0].get("course_name", "AashOfficial_Course")
        filename = f"AashOfficial - {course_name}.txt"
        
        subject_list = selected_subjects.split('&')
        video_count = 0
        
        for subject_id in subject_list:
            subject_id = subject_id.strip()
            if not subject_id:
                continue
                
            try:
                # Get topics for this subject
                topics_url = f"https://aashofficial.classx.co.in/get/alltopicfrmlivecourseclass?courseid={course_id}&subjectid={subject_id}"
                topics_response = requests.get(topics_url, headers=auth_headers)
                
                if topics_response.status_code != 200:
                    continue
                    
                topics_data = topics_response.json()
                
                if "data" not in topics_data:
                    continue
                    
                for topic in topics_data["data"]:
                    topic_name = topic.get("topic_name", "Unknown Topic")
                    topic_id = topic.get("topicid", "")
                    
                    if not topic_id:
                        continue
                        
                    # Get concepts for this topic
                    concepts_params = {
                        'courseid': course_id,
                        'subjectid': subject_id, 
                        'topicid': topic_id,
                        'start': '-1'
                    }
                    
                    concepts_url = "https://aashofficial.classx.co.in/get/allconceptfrmlivecourseclass"
                    concepts_response = requests.get(concepts_url, params=concepts_params, headers=auth_headers)
                    
                    if concepts_response.status_code != 200:
                        continue
                        
                    concepts_data = concepts_response.json()
                    
                    if "data" not in concepts_data:
                        continue
                        
                    for concept in concepts_data["data"]:
                        concept_id = concept.get("conceptid", "")
                        
                        if not concept_id:
                            continue
                            
                        # Get video details
                        video_params = {
                            'courseid': course_id,
                            'subjectid': subject_id,
                            'topicid': topic_id, 
                            'conceptid': concept_id,
                            'start': '-1'
                        }
                        
                        video_url = "https://aashofficial.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3"
                        video_response = requests.get(video_url, params=video_params, headers=auth_headers)
                        
                        if video_response.status_code != 200:
                            continue
                            
                        try:
                            video_data = video_response.json()
                            
                            if "data" not in video_data:
                                continue
                                
                            for video in video_data["data"]:
                                video_title = video.get("Title", "Unknown Video")
                                encrypted_link = video.get("download_link", "")
                                
                                if encrypted_link:
                                    try:
                                        # Attempt to decode the encrypted link
                                        decrypted_url = decode_aash(encrypted_link)
                                        video_entry = f"{video_title}:{decrypted_url}\n"
                                        
                                        with open(filename, "a", encoding="utf-8") as f:
                                            f.write(video_entry)
                                        video_count += 1
                                        
                                    except Exception as decode_error:
                                        # If decryption fails, save the encrypted link
                                        video_entry = f"{video_title}:{encrypted_link}\n"
                                        with open(filename, "a", encoding="utf-8") as f:
                                            f.write(video_entry)
                                        video_count += 1
                                        
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                error_msg = f"Error processing subject {subject_id}: {str(e)}"
                await m.reply_text(error_msg)
                continue
                
        # Send the extracted content
        if video_count > 0:
            await editable.edit(f"✅ **Extraction Complete!**\n📹 **{video_count} videos extracted**")
            
            try:
                await m.reply_document(
                    filename,
                    caption=f"🎓 **Aash Official - {course_name}**\n📹 **{video_count} videos extracted**"
                )
                os.remove(filename)
            except Exception as e:
                await m.reply_text(f"❌ **Error sending file:** {str(e)}")
        else:
            await editable.edit("❌ **No videos found or extraction failed**")
            
    except Exception as e:
        await editable.edit(f"❌ **Error:** {str(e)}")
        print(f"Aashofficial extractor error: {e}")
