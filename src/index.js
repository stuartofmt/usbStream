'use strict'

// import { registerRoute } from '../../routes'
import { registerRoute } from '@/routes'

//import Vue from 'vue';
import usbStream from './usbStream.vue'


// Register a route via Plugins -> DuetLapse3
registerRoute(usbStream, {
	Plugins: {
		DuetLapse3: {
			icon: 'mdi-transition',
			caption: 'usbStream',
			path: '/usbStream'
		}
	}
});