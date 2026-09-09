import { MOCK_PROFILE } from './mock/profile';
import type { Profile } from './types';

export interface ProfileBundle {
  profile: Profile;
  mockMode: boolean;
}

/** 启动装配：GET /api/profile；后端未起（网络/非 200/结构缺失）→ 内置 mock profile + mock 数据模式。 */
export async function loadProfile(): Promise<ProfileBundle> {
  try {
    const resp = await fetch('/api/profile');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = (await resp.json()) as Partial<Profile>;
    if (!data?.endpoint || !data?.display) throw new Error('profile 结构缺失');
    return { profile: { ...MOCK_PROFILE, ...data }, mockMode: false };
  } catch {
    return { profile: MOCK_PROFILE, mockMode: true };
  }
}
