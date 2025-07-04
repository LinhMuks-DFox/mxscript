#!/usr/bin/env python3

import subprocess
import shutil
import os

def run_cmd(cmd_list):
    subprocess.run(cmd_list, check=True)

def clean_and_rebuild():
    # 删除 ../bin
    bin_path = os.path.join("..", "bin")
    if os.path.exists(bin_path):
        print(f"Removing {bin_path}")
        shutil.rmtree(bin_path)

    # 进入 runtime/
    os.chdir("runtime")

    # 删除并新建 build/
    if os.path.exists("build"):
        print("Removing build/")
        shutil.rmtree("build")
    os.mkdir("build")
    os.chdir("build")

    # 调用 cmake，指定编译器
    print("Configuring with clang/clang++")
    run_cmd([
        "cmake",
        "-DCMAKE_C_COMPILER=clang",
        "-DCMAKE_CXX_COMPILER=clang++",
        ".."
    ])

    # 编译
    print("Building...")
    run_cmd(["cmake", "--build", "."])

if __name__ == "__main__":
    clean_and_rebuild()
