/// <reference types="vitest/globals" />
// F12：集团名称编号后缀「（NN）」拆分逻辑（编号列方案对齐前端展示）。
// 存储层 group_customer_name 含「（NN）」后缀（全角括号 + 两位零填充数字），
// 展示层把编号拆成独立元素，避免「翔宇电子华北集团（16）」读起来像脚注。
import { describe, it, expect } from 'vitest';
import { splitGroupSeq } from './riskApi';

describe('splitGroupSeq 编号后缀拆分（F12）', () => {
  it('全角括号两位数字后缀 → {基名, 编号}', () => {
    expect(splitGroupSeq('东方商贸华南集团（07）')).toEqual({ base: '东方商贸华南集团', seq: '07' });
    expect(splitGroupSeq('翔宇电子华北集团（16）')).toEqual({ base: '翔宇电子华北集团', seq: '16' });
  });

  it('无后缀名称 → {原样, null}（脚本道具集团不带编号）', () => {
    expect(splitGroupSeq('天晟集团有限公司')).toEqual({ base: '天晟集团有限公司', seq: null });
  });

  it('非两位数字后缀不误拆（防把正文当编号）', () => {
    expect(splitGroupSeq('某集团（123）')).toEqual({ base: '某集团（123）', seq: null });
  });
});
