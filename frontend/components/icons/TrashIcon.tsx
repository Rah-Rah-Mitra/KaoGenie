
import React from 'react';

interface IconProps extends React.SVGProps<SVGSVGElement> {}

export const TrashIcon: React.FC<IconProps> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12.56 0c1.153 0 2.242.078 3.223.22C6.907 5.868 6.023 6.035 5.099 6.223m7.003 0a48.64 48.64 0 0 1-7.003 0M12 12.75h.008v.008H12v-.008Z" />
  </svg>
);
    