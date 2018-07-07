#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2018 Kow Kuroda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# created by Hikaru Yokono (yokono.hikaru@jp.fujitsu.com).
#
# modified by Kow Kuroda (kow.kuroda@gmail.com), 2017/02/22, 23, 04/08
# 1. sys.stdin, stdout の wrapping処理を追加
# 2. repeat factor r の導入

import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python3')
import string
import re
import Struc
import random
import CaboCha

import io
out_enc = in_enc = "utf-8"
headersep  = ":"
sys.stdin  = io.TextIOWrapper(sys.stdin.buffer, encoding=in_enc)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=out_enc)

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="主節の述語に係る句の並びを変える")
    ap.add_argument('--debug',action='store_true',help='debug')
    ap.add_argument('--start',type=int,help='順序替えの範囲(始点)(0からカウント)',default=0)
    ap.add_argument('--end',type=int,help='順序替えの範囲(終点)',default=0)
    ## Kow Kuroda added the following three arguments.
    ap.add_argument('--repeat',type=int,help='反復回数',default=1)
    ap.add_argument('--silent',action='store_true',help='入力の非表示')
    ap.add_argument('--displace',type=int,help='スワップの回数(default 1)',default=1)
    ap.add_argument('--headersep',type=str,help='ヘッダーの区切り記号',default=':')
    args=ap.parse_args()
    cab=CaboCha.Parser('-f1')

    try:
        if args.debug: print("encoding: %s" % sys.getdefaultencoding())
        ## Kow Kuroda modified the following routine on 2017/04/08
        ## by adding loop under r = args.repeat.
        while True:
            inp=input().rstrip()
            if args.debug:
                print('Input : '+inp)
            if not args.silent:
            	print(inp + '[original]')
            # headerの分離
            try:
                header, inp = inp.split(headersep)
            except ValueError:
                header = ""; headersep = ""
            result = inp
            r = args.repeat # r は世代に相当
            d = r
            while d > 0:
                d-=1
                inp = result
                cabocha=cab.parseToString(inp)
                sentence=Struc.structure(cabocha)
                target=sentence[len(sentence)-1]['deps']
                phrase=[]
                for c in sentence:
                    temp=''
                    for m in c['morphs']:
                        line=re.split('\t',m)
                        temp+=line[0]
                    phrase.append(temp)

                for i in range(len(phrase)):
                    if i not in target and i != len(phrase)-1:
                        phrase[sentence[i]['link']]=phrase[i]+phrase[sentence[i]['link']]
                        phrase[i]=''
                phrase=[x for x in phrase if x!='']

                # 入れ替え
                # 最後のchunkは固定
                pred=phrase.pop()
                # --startと--endの範囲
                start=args.start
                end=0
                if args.end==0:
                    end=len(phrase)-1
                else:
                    end=args.end

                # 1回で何回swapさせるか(--displace)
                # startからendまでの要素の数/2が上限
                times=int(args.displace)

                # 何と何を入れ替えるかをリストで表現する．
                # 要素2個がswap1回に該当
                idx=list(range(start,end+1))
                if int(len(idx)/2)<times:
                    times=int(len(idx)/2)
                random.shuffle(idx)
                if args.debug:
                    print('swap target:',phrase)
                    print('swap list:',idx)

                pnt=0
                for n in range(0,times):
                    temp=phrase[idx[pnt]]
                    phrase[idx[pnt]]=phrase[idx[pnt+1]]
                    phrase[idx[pnt+1]]=temp
                    pnt+=2
                if args.debug:
                    print('swap result:',phrase)

                # pred=phrase.pop()
                # start=args.start
                # end=0
                # if args.end==0:
                #     end=len(phrase)-1
                # else:
                #     end=args.end
                # swap1=random.randint(start,end)
                # while True:
                #     swap2=random.randint(start,end)
                #     if swap1!=swap2:
                #         break
                # temp=phrase[swap1]
                # phrase[swap1]=phrase[swap2]
                # phrase[swap2]=temp
                # 結果の表示
                text=''.join(phrase)+pred
                print(header + headersep + text + "[with %d swaps]" % (r - d))
                # 置き換え

    except EOFError:
        pass

## end of program
