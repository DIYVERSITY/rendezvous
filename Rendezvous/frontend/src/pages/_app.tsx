import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import modernTheme from '@/themes/modernTheme';
import Layout from '@/components/Layout';
import { Lora, Merriweather, DM_Mono } from 'next/font/google';

const lora = Lora({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-lora',
});

const merriweather = Merriweather({
  subsets: ['latin'],
  weight: ['400', '700', '900'],
  display: 'swap',
  variable: '--font-merriweather',
});

const dm_mono = DM_Mono({
  subsets: ['latin'],
  weight: '400',
  display: 'swap',
  variable: '--font-dm-mono',
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <main className={`${lora.variable} ${merriweather.variable} ${dm_mono.variable}`}>
      <ThemeProvider theme={modernTheme}>
        <CssBaseline />
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </ThemeProvider>
    </main>
  );
}
