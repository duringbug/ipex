/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 13:42:29
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-14 16:57:19
 */
import { createRouter, createWebHistory } from 'vue-router'

// @ts-ignore
import App from '@/App.vue'
// @ts-ignore
import Demo01 from '@/views/Demo01.vue'
import Demo02 from '@/views/Demo02.vue'
import Demo03 from '@/views/Demo03.vue'
import Demo04 from '@/views/Demo04.vue'
import Demo05 from '@/views/02/Demo05.vue';
import Demo06 from '@/views/03/Demo06.vue';
import Demo07 from '@/views/03/Demo07.vue';
import Demo08 from '@/views/04/Demo08.vue';
import Demo09 from '@/views/05/Demo09.vue';
import Demo10 from '@/views/06/Demo10.vue';
import Demo11 from '@/views/07/Demo11.vue';
import Demo12 from '@/views/07/Demo12.vue';
import Demo13 from '@/views/08/Demo13.vue';
import Demo14 from '@/views/08/Demo14.vue';
import Demo15 from '@/views/09/Demo15.vue';
import Test01 from '@/tests/Test01.vue'
import Work01 from '@/tests/work01/Work01.vue'
import Work02 from '@/tests/work01/Work02.vue'
import Work03 from '@/tests/work01/Work03.vue'
import Work04 from '@/tests/work01/Work04.vue'
import Work05 from '@/tests/work01/Work05.vue'

const router = createRouter({
  // @ts-ignore
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'App',
      component: Work04
    },
    {
      path: '/demo01',
      name: 'Demo01',
      component: Demo01
    },
    {
      path: '/demo02',
      name: 'Demo02',
      component: Demo02
    },
    {
      path: '/demo03',
      name: 'Demo03',
      component: Demo03
    },
    {
      path: '/demo04',
      name: 'Demo04',
      component: Demo04
    },
    {
      path: '/demo05',
      name: 'Demo05',
      component: Demo05
    },
    {
      path: '/demo06',
      name: 'Demo06',
      component: Demo06
    },
    {
      path: '/demo07',
      name: 'Demo07',
      component: Demo07
    },
    {
      path: '/demo08',
      name: 'Demo08',
      component: Demo08
    },
    {
      path: '/demo09',
      name: 'demo09',
      component: Demo09
    },
    {
      path: '/demo10',
      name: 'demo10',
      component: Demo10
    },
    {
      path: '/demo11',
      name: 'demo11',
      component: Demo11
    },
    {
      path: '/demo12',
      name: 'demo12',
      component: Demo12
    },
    {
      path: '/demo13',
      name: 'demo13',
      component: Demo13
    },
    {
      path: '/demo14',
      name: 'Demo14',
      component: Demo14
    },
    {
      path: '/demo15',
      name: 'Demo15',
      component: Demo15
    },
    {
      path: '/test01',
      name: 'Test01',
      component: Test01
    },
    {
      path: '/work01',
      name: 'Work01',
      component: Work01
    },
    {
      path: '/work02',
      name: 'Work02',
      component: Work02
    },
    {
      path: '/work03',
      name: 'Work03',
      component: Work03
    },
    {
      path: '/work04',
      name: 'Work04',
      component: Work04
    },
    {
      path: '/work05',
      name: 'Work05',
      component: Work05
    }
  ]
})

export default router
