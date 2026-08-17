import {Composition} from 'remotion';
import {SkillLibrary} from './SkillLibrary';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SkillLibrary"
      component={SkillLibrary}
      durationInFrames={360}
      fps={30}
      width={1920}
      height={900}
    />
  );
};
