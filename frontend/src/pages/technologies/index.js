import { Main } from '../../components'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <iframe
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        border: 'none',
      }}
      src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=0"
      title="YouTube video"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
    />
  </Main>
}

export default Technologies
