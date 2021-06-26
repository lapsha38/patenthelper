#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2021 Andrey Golubev
import locale
import configparser
import gi
import signal
import sqlite3
import smtplib
import locale
import configparser
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


gi.require_version('Gtk', '3.0')
# gi.require_version('Gtk', '4')
from gi.repository import Gtk

# connect sqlite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
# i know that imma retarded a bit, it's ok
b0 = 0
b1 = 0
b2 = 0
b3 = 0
b4 = 0
b5 = 0
b6 = 0
b7 = 0
b8 = 0
b9 = 0
b10 = 0

class Application(object):
	def __init__(self):
		# main defs
		self.builder = Gtk.Builder()
		self.glade_file = 'ui.glade'
		self.builder.add_from_file(self.glade_file)
		self.window = self.builder.get_object('main')
		# add entry
		self.chose = self.builder.get_object('type_chose')
		self.holder = self.builder.get_object('rightHolder')
		self.name = self.builder.get_object('name')
		self.date = self.builder.get_object('date')
		self.date_chose = self.builder.get_object('date_chose')
		# buttons
		self.add_button = self.builder.get_object("add")
		self.change_button = self.builder.get_object("change")
		self.delete_button = self.builder.get_object("delete")
		# db
		self.liststore = self.builder.get_object('ListStore')
		self.view = self.builder.get_object("TreeView")
		# add data to tables:
		for row in cursor.execute("select * from patents"):
			self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
		# render gui
		self.builder.connect_signals(self)
		self.window.connect('delete-event', Gtk.main_quit)
		self.window.show_all()


	# calculate time to remind
	def calc_time(self, *args):
		# deps
		self.chose = self.builder.get_object('type_chose')
		self.date_chose = self.builder.get_object('date_chose')
		self.date = self.builder.get_object('date')
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()

		## start calc
		value_date = (datetime.strptime((self.date.get_text()), ("%d.%m.%Y")).date())
		# tm
		tm_start = value_date + relativedelta(years=9)
		tm_end = value_date + relativedelta(years=10)
		# inv
		inv_start = value_date + relativedelta(years=1)
		inv_end = value_date + relativedelta(years=2)
		# um
		um_start = value_date + relativedelta(months=6)
		um_end = value_date + relativedelta(months=11)
		# id
		if value_date < date(2015, 1, 1):
			id_start = value_date + relativedelta(years=9)
			id_end = value_date + relativedelta(years=10)
		else:
			id_start = value_date + relativedelta(years=4)
			id_end = value_date + relativedelta(years=5)
		# if combo box value = ... calc date to remind
		if self.chose.get_active() == 0:
			date_start, date_end = [tm_start, tm_end]
		elif self.chose.get_active() == 1:
			date_start, date_end = [inv_start, inv_end]
		elif self.chose.get_active() == 2:
			date_start, date_end = [um_start, um_end]
		elif self.chose.get_active() == 3:
			date_start, date_end = [id_start, id_end]

		# add years. needs to calc pay day next time
		remind_date = value_date + relativedelta(years=1)
		remind_date2 = value_date + relativedelta(years=2)

		# exclusions for pay dates
		if self.chose.get_active() == 0:
			remind_date = value_date + relativedelta(years=9)
			remind_date2 = value_date + relativedelta(years=10)
		if self.date_chose.get_active() == 1 and self.chose.get_active() == 3 and value_date < date(2015, 1, 1):
			remind_date = value_date + relativedelta(years=4)
			remind_date2 = value_date + relativedelta(years=5)

		# calc year
		remind_date_str = (date.strftime(remind_date, "%Y"))
		remind_date_str2 = (date.strftime(remind_date2, "%Y"))
		# calc day and month
		remind_day_from_table = date(1980, 1, 1)
		if self.date_chose.get_active() == 1:
			remind_day_from_table = (datetime.strptime((str(model[treeiter][5])), ("%d.%m.%Y")).date())
		remind_day = (date.strftime(remind_day_from_table, "%d.%m."))

		# convert from data format to string
		if self.date_chose.get_active() == 0:
			date_start_str = (date.strftime(date_start, "%d.%m.%Y"))
			date_end_str = (date.strftime(date_end, "%d.%m.%Y"))
		# sum of 2 strings to make a date
		if self.date_chose.get_active() == 1:
			date_start_str = remind_day + remind_date_str
			date_end_str = remind_day + remind_date_str2
		return date_start_str, date_end_str

	# add sql connect
	def create_table(self, create_button):
		cursor = conn.cursor()
		# sql query (add table)
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS patents(
			"id"	INTEGER NOT NULL UNIQUE,
			"type"	TEXT NOT NULL,
			"numCert"	NUMERIC NOT NULL UNIQUE,
			"name"	TEXT NOT NULL,
			"rightholder"	TEXT NOT NULL,
			"priorityDate"	TEXT NOT NULL,
			"pdUpdateStart"	TEXT,
			"pdUpdateEnd"	TEXT,
			"payDate"	TEXT,
			"email"	TEXT,
			"sended"	INTEGER,
			"dateISO"	REAL
		""")
		conn.commit()
		cursor.close()

	# connect buttons (gui) and code
	# add button
	def click_add(self, add):
		cursor = conn.cursor()
		# input variables from __init__
		self.chose = self.builder.get_object('type_chose')
		self.number = self.builder.get_object('certNum')
		self.holder = self.builder.get_object('rightHolder')
		self.name = self.builder.get_object('name')
		self.date_chose = self.builder.get_object('date_chose')
		self.date = self.builder.get_object('date')
		self.email = self.builder.get_object('email')
		self.note = self.builder.get_object('note')
		# time calc
		calc_time = self.calc_time()
		# get column count to set id
		value_id = len(self.liststore) + 1
		# another colums for import to table
		value_chose = (self.chose.get_active_text())
		value_number = int(self.number.get_text())
		value_name = (self.name.get_text())
		value_holder = (self.holder.get_text())
		value_email = (self.email.get_text())
		value_note = (self.note.get_text())

		iter = self.liststore.append()
		# add data from form to table
		self.liststore.set(iter, 0, (value_id))
		self.liststore.set(iter, 1, (value_chose))
		self.liststore.set(iter, 2, (value_number))
		self.liststore.set(iter, 3, (value_name))
		self.liststore.set(iter, 4, (value_holder))
		self.liststore.set(iter, 5, self.date.get_text())
		# calculate date of ending patents and add it to table
		self.liststore.set(iter, 6, (calc_time[0]))
		self.liststore.set(iter, 7, (calc_time[1]))
		# if client pay 1 time, we add it to base
		if self.date_chose.get_active() == 1:
			self.liststore.set(iter, 8, (self.date.get_text()))
		self.liststore.set(iter, 9, (value_email))
		self.liststore.set(iter, 10, (value_note))

		date_start_str_iso = (datetime.strptime((calc_time[0]), ("%d.%m.%Y")).date())
		date_end_str_iso = ((datetime.strptime((calc_time[1]), ("%d.%m.%Y")).date()) + relativedelta(months=6))
		priority_date_iso = (datetime.strptime((self.date.get_text()), ("%d.%m.%Y")).date())

		cursor.execute("""INSERT into patents (id,type,numCert,name,rightholder,priorityDate,pdUpdateStart,pdUpdateEnd,email,dateISO,dateEND,nextRemind,note,priorityDate_ISO) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
			""", (value_id, value_chose, value_number, value_name, value_holder, (self.date.get_text()), calc_time[0],
				  calc_time[1], value_email, date_start_str_iso, date_end_str_iso, date_start_str_iso, value_note, priority_date_iso))
		conn.commit()
		cursor.close()

	# edit button
	def click_edit(self, change):
		self.date = self.builder.get_object('date')
		# time calc
		calc_time = self.calc_time()
		# get column count to set id
		value_id = len(self.liststore) + 1
		# another colums for import to table
		value_chose = (self.chose.get_active_text())
		value_number = int(self.number.get_text())
		value_name = (self.name.get_text())
		value_holder = (self.holder.get_text())
		# don't wanna 'none' in a row, will be better if row is empty
		if self.email.get_text() is not None:
			value_email = (self.email.get_text())
		if self.note.get_text() is not None:
			value_note = (self.note.get_text())

		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		date_start_str_iso = (datetime.strptime((calc_time[0]), ("%d.%m.%Y")).date())
		date_end_str_iso = (datetime.strptime((calc_time[1]), ("%d.%m.%Y")).date())
		i = (model[treeiter][0])

		# push values to db
		cursor = conn.cursor()
		cursor.execute("""UPDATE patents SET type = '{0}', numCert = '{1}', name = '{2}', 
			rightholder = '{3}', pdUpdateStart = '{4}', 
			pdUpdateEnd = '{5}', email = '{6}', dateISO = '{7}', dateEND = '{8}', note = '{9}' WHERE id = '{10}'
			""".format(value_chose, value_number, value_name, value_holder, calc_time[0],
					   calc_time[1], value_email, date_start_str_iso, date_end_str_iso, value_note, i))
		if self.date_chose.get_active() == 0:
			cursor.execute("""UPDATE patents SET priorityDate = '{0}', sended = 0, priorityDate_ISO = '{1}' WHERE id = '{2}'
			""".format(self.date.get_text(), (datetime.strptime((self.date.get_text()), ("%d.%m.%Y")).date()), i))
		if self.date_chose.get_active() == 1:
			cursor.execute("""UPDATE patents SET payDate = '{0}', sended = 0, payDate_ISO = '{1}' WHERE id = '{2}'
			""".format(self.date.get_text(), (datetime.strptime((self.date.get_text()), ("%d.%m.%Y")).date()), i))
		conn.commit()
		cursor.close()
		# push values to table gui
		self.liststore.set(treeiter, 1, (value_chose))
		self.liststore.set(treeiter, 2, (value_number))
		self.liststore.set(treeiter, 3, (value_name))
		self.liststore.set(treeiter, 4, (value_holder))
		if self.date_chose.get_active() == 0:
			self.liststore.set(treeiter, 5, (self.date.get_text()))
		self.liststore.set(treeiter, 6, (calc_time[0]))
		self.liststore.set(treeiter, 7, (calc_time[1]))
		if self.date_chose.get_active() == 1:
			self.liststore.set(treeiter, 8, (self.date.get_text()))
		self.liststore.set(treeiter, 9, (value_email))
		self.liststore.set(treeiter, 10, (value_note))

	# get values from table
	def on_clicked(self, clicked):
		select = self.builder.get_object("TreeView").get_selection()
		self.number = self.builder.get_object('certNum')
		self.holder = self.builder.get_object('rightHolder')
		self.name = self.builder.get_object('name')
		self.date_chose = self.builder.get_object('date_chose')
		self.date = self.builder.get_object('date')
		self.email = self.builder.get_object('email')
		self.note = self.builder.get_object('note')
		model, treeiter = select.get_selected()
		# set data to entrys
		i1 = (model[treeiter][1])
		if i1 == 'Товарный знак':
			self.chose.set_active(0)
		elif i1 == 'Изобретение':
			self.chose.set_active(1)
		elif i1 == 'Полезная модель':
			self.chose.set_active(2)
		elif i1 == 'Промышленный образец':
			self.chose.set_active(3)
		self.number.set_text(str(model[treeiter][2]))
		self.holder.set_text(str(model[treeiter][4]))
		self.name.set_text(str(model[treeiter][3]))
		# if no pay date => set priority date as main
		if str(model[treeiter][8]) == 'None':
			self.date_chose.set_active(0)
			self.date.set_text(str(model[treeiter][5]))
		else:
			self.date_chose.set_active(1)
			self.date.set_text(str(model[treeiter][8]))
		# hide email if data is empty
		if str(model[treeiter][9]) == 'None' or str(model[treeiter][9]) == '':
			self.note.set_text('')
		else:
			self.note.set_text(str(model[treeiter][9]))
		# same for note
		if str(model[treeiter][10]) == 'None' or str(model[treeiter][10]) == '':
			self.note.set_text('')
		else:
			self.note.set_text(str(model[treeiter][10]))


	def on_search(self, search):
		global b0
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b0 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by id DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b0 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by id ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b0 -= 1
		cursor.close()
	def on_search1(self, search):
		global b1
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b1 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by type DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b1 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by type ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b1 -= 1
		cursor.close()
	def on_search2(self, search):
		global b2
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b2 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by numCert DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b2 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by numCert ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b2 -= 1
		cursor.close()
	def on_search3(self, search):
		global b3
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b3 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by name DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b3 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by name ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b3 -= 1
		cursor.close()
	def on_search4(self, search):
		global b4
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b4 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by rightholder DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b4 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by rightholder ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b4 -= 1
		cursor.close()
	def on_search5(self, search):
		global b5
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b5 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by priorityDate_ISO DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b5 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by priorityDate_ISO ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b5 -= 1
		cursor.close()
	def on_search6(self, search):
		global b6
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b6 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by dateISO DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b6 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by dateISO ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b6 -= 1
		cursor.close()
	def on_search7(self, search):
		global b7
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b7 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by dateEND DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b7 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by dateEND ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b7 -= 1
		cursor.close()
	def on_search8(self, search):
		global b8
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b8 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by payDate_ISO DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b8 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by payDate_ISO ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b8 -= 1
		cursor.close()
	def on_search9(self, search):
		global b9
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b9 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by email DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b9 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by email ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b9 -= 1
		cursor.close()
	def on_search10(self, search):
		global b10
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		self.liststore.clear()
		cursor = conn.cursor()
		if b10 % 2 == 0:
			for row in cursor.execute("SELECT * FROM patents ORDER by note DESC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
			b10 += 1
		else:
			for row in cursor.execute("SELECT * FROM patents ORDER by note ASC"):
				self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])    
			b10 -= 1
		cursor.close()

	# del button connect
	def click_del(self, delete):
		cursor = conn.cursor()
		self.date_chose = self.builder.get_object('date_chose')
		# get id for selected row
		select = self.builder.get_object("TreeView").get_selection()
		model, treeiter = select.get_selected()
		i = (model[treeiter][0])
		# del row from db
		if treeiter is not None:
			sql_delete_query = """DELETE from patents where id = ?"""
		cursor.execute(sql_delete_query, ((model[treeiter][0]),))
		# set right id to rows after delete
		cursor.execute("UPDATE patents SET id = id - 1 WHERE id > '%s'" % i)
		conn.commit()
		id_for_change = self.liststore.get_value(treeiter, 0)
		self.liststore.remove(treeiter)
		# refresh list after delete
		self.liststore.clear()
		for row in cursor.execute("select * from patents"):
			self.liststore.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
		cursor.close()

	# destroy button with sql connect close
	def onDestroy(self, *args):
		Gtk.main_quit()
		conn.close()


class SelectTable:
	@staticmethod
	# select table from db
	def sql_select_to_list(num, select_table):
		cursor = conn.cursor()
		list_n = []
		cursor.execute("SELECT %s FROM patents WHERE sended < 6 AND nextRemind < date('now') ORDER BY nextRemind" % (select_table,))
		list_sql = cursor.fetchall()
		for row in list_sql:
				list_n.append(row[0])
		cursor.close()
		return(list_n[num])

	# change next_remind date
	def next_remind():
		cursor = conn.cursor()
		cursor.execute("""
			UPDATE patents set nextRemind = CASE
			WHEN nextRemind is NULL THEN dateISO
			ELSE nextRemind
			END """)
		conn.commit()
		cursor.close()

	# get number of rows
	def countRows():
			cursor = conn.cursor()
			cursor.execute("SELECT COUNT(*) numCert FROM patents WHERE sended < 6 AND nextRemind < date('now') ORDER BY nextRemind")
			len_list = cursor.fetchone()
			cursor.close()
			return len_list[0]

	def setSended():
		cursor = conn.cursor()
		cursor.execute("UPDATE patents SET sended = sended + 1 WHERE sended < 6 AND nextRemind < date('now')")
		cursor.execute(
				"UPDATE patents SET nextRemind = DATE(('now'), '+3 month') WHERE sended < 6 AND nextRemind < date('now')")
		conn.commit()
		cursor.close()

	next_remind()

class TxtFile:
	def make_txt_file(len_list):
		# if list is not null, make some text file
		if len_list != 0:
			# fill list for remind
			mail_file = open("LastMail.txt", "w")
			for num in range(len_list):
				message = (str(num + 1) + '. ' + str(
					SelectTable.sql_select_to_list(num, 'type')) + '; Наименование: ' + str(
					SelectTable.sql_select_to_list(num, 'name')) + '; Правообладатель: ' + str(
					SelectTable.sql_select_to_list(num, 'rightholder')) + '; Номер: ' + str(
					SelectTable.sql_select_to_list(num, 'numCert')) + '; Дата приоритета: ' + str(
					SelectTable.sql_select_to_list(num, 'priorityDate')) + '; Дата последнего платежа: ' + str(
					SelectTable.sql_select_to_list(num, 'payDate')) + '; Оплатить с: ' + str(
					SelectTable.sql_select_to_list(num, 'pdUpdateStart')) + '; Оплатить по: ' + str(
					SelectTable.sql_select_to_list(num, 'pdUpdateEnd')) 
					# + '; Отправить на почту: ' + str(
					#SelectTable.sql_select_to_list(num, 'email')) + '; Примечание: ' + str(
					#SelectTable.sql_select_to_list(num, 'note'))
					+ '\n')

				mail_file.write(message)
			mail_file.close()
	make_txt_file(SelectTable.countRows())

class MessageDialogWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="MessageDialog Example")

		dialog = Gtk.MessageDialog(
			transient_for=self,
			flags=0,
			message_type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			text="This is an INFO MessageDialog",
		)
		dialog.format_secondary_text(
			"And this is the secondary text that explains things."
		)
		dialog.run()
		print("INFO dialog closed")

		dialog.destroy()

class SendMail:
	# get month name to subject of mail
	def month_name():
		#set russian locale
		locale.setlocale(locale.LC_TIME, "ru_RU")
		current_month = (date.strftime((datetime.today()), "%B").lower())
		return(current_month)

	def read_config():
		# read configs from settings.ini
		config = configparser.ConfigParser()
		config.read("settings.ini")
		# from
		message_from = config["Mail"]["from"]
		# pass
		password = config["Mail"]["password"]
		# to
		message_to = config["Mail"]["to"]
		return(message_from, password, message_to)

	def send_email(month, message_from, password, message_to):
		# Subject of the mail
		subject = "Напоминание за %s" % (month)
		msg = MIMEMultipart()
		msg['Subject'] = subject
		# get info from read_config
		msg['From'] = message_from
		password = password
		msg['To'] = message_to
		# read info from txt file and pass it to message
		mail_file = open("LastMail.txt")
		msg.attach(MIMEText(mail_file.read(), 'plain'))
		# try to login gmail for sending the mail
		win = MessageDialogWindow()
		win.connect("destroy", Gtk.main_quit)
		try:
			server = smtplib.SMTP('smtp.gmail.com: 587')
			server.starttls()
			server.login(msg['From'], password)
			server.sendmail(msg['From'], msg['To'], msg.as_string())
			server.quit()
			mail_file.close()
			# make a mark about sended objects
			SelectTable.setSended()
		except:
			print('error')

	send_email(month_name(), read_config()[0], read_config()[1], read_config()[2])



if __name__ == '__main__':
	SendMail()
	Application()
	Gtk.main()