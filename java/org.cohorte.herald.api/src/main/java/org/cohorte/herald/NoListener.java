/**
 * Copyright 2014 isandlaTech
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.cohorte.herald;


/**
 * The message has been received by the remote peer, but no listener has been
 * found to register it.
 *
 * @author Thomas Calmant
 */
public class NoListener extends HeraldException {

    /** Serialization version UID */
    private static final long serialVersionUID = 1L;

    /** Original message UID */
    private final String pMessageUid;

    /** Subject of the original message */
    private final String pSubject;

    /**
     * Sets up the exception
     *
     * @param aTarget
     *            Targeted peer(s)
     * @param aMessageUid
     *            Original message UID
     * @param aSubject
     *            Subject of the original message
     */
    public NoListener(final Target aTarget, final String aMessageUid,
            final String aSubject) {

        super(aTarget, "No listener for " + aMessageUid);
        pMessageUid = aMessageUid;
        pSubject = aSubject;
    }

    /**
     * @return the subject
     */
    public String getSubject() {

        return pSubject;
    }

    /**
     * @return the messageUid
     */
    public String getUid() {

        return pMessageUid;
    }
}
