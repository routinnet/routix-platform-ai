import type { Metadata, Viewport } from 'next'
import { Inter, Poppins } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({ 
  weight: ['300', '400', '500', '600', '700', '800'],
  subsets: ['latin'],
  variable: '--font-poppins',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Routix - AI-Powered Thumbnail Generator',
  description: 'Create stunning YouTube thumbnails with AI. Chat-based interface powered by advanced AI algorithms.',
  keywords: 'thumbnail generator, AI, content creation, YouTube, Instagram, ChatGPT, DALL-E, Midjourney',
  authors: [{ name: 'Routix Team' }],
  openGraph: {
    title: 'Routix - AI-Powered Thumbnail Generator',
    description: 'Create stunning thumbnails with AI',
    type: 'website',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: '#667eea',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body className={poppins.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
