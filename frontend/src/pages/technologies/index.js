import { Main } from '../../components'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '80vh',
      padding: '20px',
    }}>
      <iframe
        width="800"
        height="450"
        src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=0"
        title="YouTube video"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        style={{
          maxWidth: '100%',
          borderRadius: '12px',
        }}
      />
    </div>
  </Main>
}

export default Technologies
