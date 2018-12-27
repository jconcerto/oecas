#!/usr/bin/env python

import filecmp
import importlib
import unittest
import os

TEST_DIR = os.getcwd() + '/Tests'
INPUT_DIR = TEST_DIR + '/SampleInputFiles'
EXPECTED_DIR = TEST_DIR + '/ExpectedOutputFiles'
TEMPLATES = TEST_DIR + '/SampleTemplates'
OUTPUT_DIR = TEST_DIR + '/temp'

parse_csv = importlib.import_module("oecas_external.parse_csv")

class Parse(unittest.TestCase):

	def test_no_values_filled(self):
		parse_csv.parse("no_values.csv", OUTPUT_DIR, INPUT_DIR, TEMPLATES + "/Template1.xml")
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/testing.xml", EXPECTED_DIR + "/novalue_testing.xml"))
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/no value.xml", EXPECTED_DIR + "/novalue_no value.xml"))

	def test_all_values_filled(self):
		parse_csv.parse("all_values.csv", OUTPUT_DIR, INPUT_DIR, TEMPLATES + "/Template1.xml")
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/line1.xml", EXPECTED_DIR + "/allvalues_line1.xml"))
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/line2.xml", EXPECTED_DIR + "/allvalues_line2.xml"))

	def test_some_values_filled(self):
		parse_csv.parse("some_values.csv", OUTPUT_DIR, INPUT_DIR, TEMPLATES + "/Template2.xml")
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/line1.xml", EXPECTED_DIR + "/somevalues_line1.xml"))
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/line2.xml", EXPECTED_DIR + "/somevalues_line2.xml"))
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/line3.xml", EXPECTED_DIR + "/somevalues_line3.xml"))

	def test_duplicate_names(self):
		parse_csv.parse("dupe_names.csv", OUTPUT_DIR, INPUT_DIR, TEMPLATES + "/Template1.xml")
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/name1.xml", EXPECTED_DIR + "/dupe_name1.xml"))
		self.assertTrue(filecmp.cmp(OUTPUT_DIR+"/name2.xml", EXPECTED_DIR + "/dupe_name2.xml"))
