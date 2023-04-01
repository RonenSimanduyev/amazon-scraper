import { routes } from "../routes";
import { useState } from 'react';

export const HomePage = () => {
    const [amazonLink, setAmazonLink] = useState('');

    const sendLink = async (e) => {
        e.preventDefault();
        const response = await fetch(`${routes.server}/runScript`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amazonLink })
        });

        const data = await response.json();
        console.log(data);
    };


    return (
        <div>
            <h1>
                insert a link
            </h1>
            <form onSubmit={sendLink}>
                <input type="text" name='amazonLink' value={amazonLink} onChange={(e) => setAmazonLink(e.target.value)} />
                <button type="submit" className="btn btn-primary"> submit</button>
            </form>
            <div>

            </div>
        </div>
    )
}