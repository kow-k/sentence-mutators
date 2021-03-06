#!/usr/bin/env python3
# coding: utf-8

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


import os
import sys
#sys.path.append(os.environ['HOME']+'/lib/python')
import string
import re
import MeCab

if __name__=='__main__':
    import argparse
    # コマンドラインオプション
    ap=argparse.ArgumentParser(description="textをword2vecの学習用データにする(分かち書きしてひとまとめ)")
    ap.add_argument('file',type=open,metavar='FILE',help='1行1文')
    ap.add_argument('--stem','-s',action='store_true',help='動詞，形容詞を基本形に戻す')
    ap.add_argument('--pos','-p',action='store_true',help='品詞情報付き')
    ap.add_argument('--mecabopt',type=str,metavar='STRING',help='mecabのオプション',default='')
    args=ap.parse_args()

    tagger=MeCab.Tagger(args.mecabopt)

    for ln in args.file:
        ln=ln.rstrip()
        ln=re.sub('^　','',ln)
        morphs=re.split('\n',tagger.parse(ln).rstrip())
        morphs.pop()
        result=[]
        for m in morphs:
            line=re.split('\t',m)
            features=re.split(',',line[1])
            if args.stem and re.match('動詞|形容詞',features[0]):
                result.append(features[6])
            if args.pos:
                base=line[0]
                if features[6] != '*':
                    base=features[6]
                pos=features[0]
                if re.match('動詞|形容詞|助動詞',features[0]):
                    pos+='-'+features[4]
                result.append(base+'-'+pos)
            else:
                result.append(line[0])
        print(' '.join(result))
