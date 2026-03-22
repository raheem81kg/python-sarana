# 🚀 Quick Start Guide — Sarana Compiler

## Step 1: Install Dependencies (1 minute)

```bash
cd python-sarana
pip install -r requirements.txt
```

If you get permission errors on Mac, use:
```bash
pip install --break-system-packages -r requirements.txt
```

---

## Step 2: Test Everything Works (1 minute)

```bash
python3 run_all_tests.py
```

You should see:
```
✓✓✓ ALL TESTS PASSED ✓✓✓
Total: 79/79 tests passed
```

---

## Step 3: Run the Web UI (30 seconds)

```bash
streamlit run app/ui.py
```

Your browser will automatically open to `http://localhost:8501`

**What you'll see:**
- Sarana playground
- Sample programs in dropdown
- 6 interactive tabs
- Real-time compilation

---

## Step 4: Try a Sample Program (30 seconds)

In the web UI:
1. Select " Sample 1: Required Demo" from dropdown
2. Click " Run Sarana"
3. See output in " Output" tab
4. Explore other tabs (Tokens, AST, etc.)

---

## Step 5: Use Command Line (30 seconds)

```bash
# Compile and run a program
python3 src/sarana.py samples/sample1.sa

# You'll see:
# Error: Division by zero attempted but not allowed.
# The result is  1620
# ✅ Compiled successfully: samples/sample1.py

# Run the generated Python code
python3 samples/sample1.py

# Same output!
```

---

## 🎯 Common Tasks

### Write Your Own Sarana Program

Create a file `myprogram.sa`:
```sarana
bloom x = 10;
bloom y = 20;
echo "The sum is:" (x + y);
```

Run it:
```bash
python3 src/sarana.py myprogram.sa
python3 myprogram.py  # Run generated code
```

---

### Run Individual Tests

```bash
python3 test_1_errors.py      # Test error classes
python3 test_2_lexer.py        # Test tokenization
python3 test_3_parser.py       # Test parser
python3 test_4_semantic.py     # Test semantic analyzer
python3 test_5_interpreter.py  # Test interpreter
python3 test_6_full_pipeline.py # Test full compiler
python3 test_7_codegen.py      # Test code generator
python3 test_8_main_entry.py   # Test main entry point
```

---

### Generate Parse Trees (For Report)

```bash
python3 generate_parse_tree.py
cat PARSE_TREE_DIAGRAMS.txt
```

---

### View Generated Python Code

All generated `.py` files are in the `samples/` folder:
```bash
cat samples/sample1.py
```

---

## 🐛 Troubleshooting

### If Streamlit doesn't start:
```bash
# Make sure you're in the right directory
cd python-sarana
pwd  # Should end in "python-sarana"

# Try with full path
streamlit run app/ui.py
```

### If imports fail:
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Check Python version (need 3.8+)
python3 --version
```

### If tests fail:
```bash
# Make sure you're in the project root
cd python-sarana

# Run a single test to see detailed error
python3 test_1_errors.py
```

---

## 📱 Web UI Features Quick Guide

### Left Sidebar
- **Sample Programs** — Load pre-written examples
- **Compiler Options** — Enable/disable interpreter or codegen
- **LLM Integration** — Compare with Claude (requires API key)
- **Language Reference** — Quick keyword/operator reference

### Main Tabs
1. **🎯 Output** — What your program prints
2. **🔤 Tokens** — See how lexer tokenizes your code
3. **🌳 AST** — View the abstract syntax tree
4. **✓ Semantic** — Static error checking results
5. **🐍 Generated** — Python code you can download
6. **🤖 LLM** — Compare Sarana vs Claude output

---

## 🎓 For Presentation

### Demo Script (5 minutes)

1. **Open Web UI**
   ```bash
   streamlit run app/ui.py
   ```

2. **Show Sample 1** (Required Assignment)
   - Select from dropdown
   - Click Run
   - Show Output tab (1620)
   - Show Generated Code tab
   - Click Download button

3. **Show Tokens Tab**
   - Explain color coding
   - Point out keywords, literals, operators

4. **Show AST Tab**
   - Explain tree structure
   - Point out PEMDAS (+ is root, * is nested)

5. **Show Semantic Tab**
   - Show "No errors" message
   - Explain what it checks

6. **Try a Sample with Error**
   - Type: `echo x;` (undefined variable)
   - Click Run
   - Show semantic error with line number

7. **Show Command Line**
   ```bash
   python3 src/sarana.py samples/sample3.sa
   ```
   - Show output (factorial, fibonacci)

8. **Show Generated Code Works**
   ```bash
   python3 samples/sample3.py
   ```
   - Same output!

---

## 📊 Testing for Grading

To verify everything works for graders:

```bash
# 1. Run all tests
python3 run_all_tests.py

# 2. Run each sample
python3 src/sarana.py samples/sample1.sa
python3 src/sarana.py samples/sample2.sa
python3 src/sarana.py samples/sample3.sa
python3 src/sarana.py samples/sample4.sa

# 3. Verify generated code works
python3 samples/sample1.py
python3 samples/sample2.py
python3 samples/sample3.py
python3 samples/sample4.py

# 4. Launch web UI
streamlit run app/ui.py
```

All should work without errors!

---

## ⏱️ Time Estimates

- Install: 1 minute
- Run tests: 1 minute
- Launch UI: 30 seconds
- Try samples: 2 minutes
- **Total: ~5 minutes to verify everything works**

---

## 🎯 Success Checklist

- [ ] All 79 tests pass
- [ ] Web UI launches without errors
- [ ] All 4 sample programs compile and run
- [ ] Generated Python files execute correctly
- [ ] Parse tree generator works
- [ ] Command-line tool works
- [ ] README is updated with group names

---

**You're ready to demo and submit!** 🎉
